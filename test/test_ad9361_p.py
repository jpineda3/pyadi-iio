import pytest
import os

hardware = ["packrf", "adrv9361", "fmcomms2", "ad9361"]
classname = "adi.ad9361"

#########################################
@pytest.mark.iio_hardware(hardware)
@pytest.mark.parametrize("classname", [(classname)])
@pytest.mark.parametrize("param", [True, True, True])
def test_ad9361_parametrized_True(param, classname):
    assert param == True


#########################################
@pytest.mark.iio_hardware(hardware)
@pytest.mark.parametrize("classname", [(classname)])
def test_ad9361_pass_in_rerun(classname):
    try:
        assert (os.environ.get('VAR_THAT_EXISTS_ONLY_AFTER_FAILURE'))
    except AssertionError:
        os.environ['VAR_THAT_EXISTS_ONLY_AFTER_FAILURE'] = 'EXISTING_VAR'
        raise AssertionError

#########################################
@pytest.mark.iio_hardware(hardware)
@pytest.mark.parametrize("classname", [(classname)])
@pytest.mark.parametrize("param", [True, True, True])
def test_ad9361_sandwich_passing(param,classname):
    assert param == True

#########################################
@pytest.mark.iio_hardware(hardware)
@pytest.mark.parametrize("classname", [(classname)])
def test_ad9361_known_failing(classname):
    raise AssertionError
