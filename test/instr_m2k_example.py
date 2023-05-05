import time

import instr_m2k

# ################### Signal Generator ###################
# # Create signal generator instrument from ip uri
# m2k_uri='ip:192.168.2.1'
# m2k_ctx = instr_m2k.connect(uri=m2k_uri,calibrate=False)
# siggen = instr_m2k.create_instr(m2k_ctx,"siggen")

# # Control signal generator
# instr_m2k.control(siggen,0,[30000,0.5, 0,0])
# instr_m2k.control(siggen,1,[50000,0.5, 0,0])

# instr_m2k.contextClose(m2k_ctx)

# ################### Spectrum Analyzer ###################
# # Create spectrum analyzer instrument from ip uri
# m2k_uri='ip:192.168.2.1'
# m2k_ctx = instr_m2k.connect(uri=m2k_uri,calibrate=False)
# specanalyzer = instr_m2k.create_instr(m2k_ctx,"specanalyzer")

# # Control signal generator
# freq_est0 = instr_m2k.control(specanalyzer,0,[2000000])
# print(f"Estimated frequency at channel 1: {freq_est0} Hz")
# freq_est1 = instr_m2k.control(specanalyzer,1,[3000000])
# print(f"Estimated frequency at channel 1: {freq_est1} Hz")

# instr_m2k.contextClose(m2k_ctx)

################### Voltmeter ###################
# Create voltmeter instrument from ip uri
m2k_uri = "ip:192.168.2.1"
m2k_ctx = instr_m2k.connect(uri=m2k_uri, calibrate=False)
voltmeter = instr_m2k.create_instr(m2k_ctx, "voltmeter")

# Control signal generator
volt0 = instr_m2k.control(voltmeter, 0)
print(f"Voltage at channel 0: {volt0} V")
volt1 = instr_m2k.control(voltmeter, 1)
print(f"Voltage at channel 1: {volt1} V")

instr_m2k.contextClose(m2k_ctx)

# ################### Power supply ###################
# # Create power supply instrument from ip uri
# m2k_uri = "ip:192.168.2.1"
# m2k_ctx = instr_m2k.connect(uri=m2k_uri, calibrate=False)
# ps = instr_m2k.create_instr(m2k_ctx, "powersupply")

# # Control signal generator
# volt0 = instr_m2k.control(ps, 0, [2, True])
# volt1 = instr_m2k.control(ps, 1, [-4, True])

# time.sleep(5)

# instr_m2k.contextClose(m2k_ctx)
