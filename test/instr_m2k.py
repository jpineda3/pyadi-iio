import heapq
import math
import time

import libm2k
import numpy as np
import rf.spec as spec

DAC_available_sample_rates = [750, 7500, 75000, 750000, 7500000, 75000000]
DAC_max_rate = DAC_available_sample_rates[-1]  # last sample rate = max rate
DAC_min_nr_of_points = 10
max_buffer_size = 500000
ADC_available_sample_rates = [1000, 10000, 100000, 1000000, 10000000, 100000000]
ADC_max_rate = ADC_available_sample_rates[-1]  # last sample rate = max rate
ADC_min_nr_of_points = 10


def connect(uri, calibrate):
    ctx = libm2k.m2kOpen(uri)
    if ctx is None:
        print("Connection Error: No ADALM2000 device available/connected to your PC.")
        exit(1)

    if calibrate:
        ctx.calibrateDAC()
        ctx.calibrateADC()

    return ctx


def get_best_ratio(ratio):
    max_it = max_buffer_size / ratio
    best_ratio = ratio
    best_fract = 1

    for i in range(1, int(max_it)):
        new_ratio = i * ratio
        (new_fract, integral) = math.modf(new_ratio)
        if new_fract < best_fract:
            best_fract = new_fract
            best_ratio = new_ratio
        if new_fract == 0:
            break

    return best_ratio, best_fract


def get_samples_count(rate, freq, mode):
    ratio = rate / freq

    if mode == "DAC":
        min_nr_of_points = DAC_min_nr_of_points
        max_rate = DAC_max_rate
    elif mode == "ADC":
        min_nr_of_points = ADC_min_nr_of_points
        max_rate = ADC_max_rate

    if ratio < min_nr_of_points and rate < max_rate:
        return 0
    if ratio < 2:
        return 0

    ratio, fract = get_best_ratio(ratio)
    # ratio = number of periods in buffer
    # fract = what is left over - error

    size = int(ratio)
    while size & 0x03:
        size = size << 1
    while size < 1024:
        size = size << 1
    return size


def get_optimal_sample_rate(freq, mode):
    if mode == "DAC":
        available_sample_rates = DAC_available_sample_rates
    elif mode == "ADC":
        available_sample_rates = ADC_available_sample_rates

    for rate in available_sample_rates:
        buf_size = get_samples_count(rate, freq, mode)
        if buf_size:
            return rate


def sine_buffer_generator(freq, ampl, offset, phase):

    buffer = []

    sample_rate = get_optimal_sample_rate(freq, "DAC")
    nr_of_samples = get_samples_count(sample_rate, freq, "DAC")
    samples_per_period = sample_rate / freq
    phase_in_samples = (phase / 360) * samples_per_period

    for i in range(nr_of_samples):
        buffer.append(
            offset
            + ampl
            * (math.sin(((i + phase_in_samples) / samples_per_period) * 2 * math.pi))
        )

    return sample_rate, buffer


def estimate_frequency(signal, sampling_rate):
    # Compute the FFT of the signal
    spectrum = np.fft.fft(signal)

    # Compute the power spectrum
    power_spectrum = np.abs(spectrum) ** 2

    # Find the frequency corresponding to the maximum value in the power spectrum
    max_index = np.argmax(power_spectrum)
    max_frequency = max_index * sampling_rate / len(signal)

    return max_frequency


def create_instr(ctx, instrument):
    # Method to create instrument object from ctx
    if instrument == "siggen":
        instr = ctx.getAnalogOut()
    elif instrument == "specanalyzer" or instrument == "voltmeter":
        instr = ctx.getAnalogIn()
    elif instrument == "powersupply":
        instr = ctx.getPowerSupply()

    return instr


def control(instr, chan, control_param=None):
    # Generic control method for any instrument
    #   instr - instrument object
    #   chan - ADC or DAC channel, 0 or 1 only
    #   control_param - a list containing control parameters
    #       siggen - [tone_frequency,ampl,offset,phase]
    #       voltmeter - None
    #       power supply - [voltage,apply_calibration]
    #       spectrum analyzer - [expected_tone_frequency]

    if isinstance(instr, libm2k.M2kAnalogOut) and len(control_param) == 4:
        # Generates sinewave at chan
        # Known issue - signal generated at one channel appears at the other
        tone_frequency, ampl, offset, phase = control_param
        samp, buffer = sine_buffer_generator(tone_frequency, ampl, offset, phase)
        instr.enableChannel(chan, True)
        instr.setSampleRate(chan, samp)
        instr.push(chan, buffer)

        return

    elif isinstance(instr, libm2k.M2kAnalogIn) and control_param == None:
        # Reads voltage at chan
        # Prevent bad initial config
        instr.reset()
        instr.enableChannel(chan, True)

        return instr.getVoltage(chan)

    elif isinstance(instr, libm2k.M2kPowerSupply):
        # Sets power supply voltage at chan
        voltage, cal = control_param
        instr.enableChannel(chan, True)
        instr.pushChannel(chan, voltage, cal)

        return

    elif isinstance(instr, libm2k.M2kAnalogIn) and len(control_param) == 1:
        # Returns frequency estimate received in chan
        # Known issue - Cannot estimate frequency at second consecutive method calls
        # at different channels when one frequency is at least 10x larger
        expected_tone_frequency = control_param[0]
        estimated_frequency = []
        instr.enableChannel(chan, True)
        samp = get_optimal_sample_rate(expected_tone_frequency, "ADC")
        nr_of_samples = get_samples_count(samp, expected_tone_frequency, "ADC")
        instr.setSampleRate(samp)
        instr.setRange(0, -10, 10)
        num_read = 3

        for i in range(num_read):
            data = instr.getSamples(nr_of_samples)
            time.sleep(0.1)
            tone_peaks, tone_freqs = spec.spec_est(data[chan], fs=samp, ref=2 ** 15)
            indx = heapq.nlargest(2, range(len(tone_peaks)), tone_peaks.__getitem__)
            peak = tone_freqs[indx[0]]
            estimated_frequency.append(peak)
        estimated_frequency = np.mean(estimated_frequency)
        instr.enableChannel(chan, False)

        return estimated_frequency


def contextClose(ctx):
    libm2k.contextClose(ctx)
