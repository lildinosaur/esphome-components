import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import i2c, esp32
from esphome.const import CONF_ID

CODEOWNERS = ["@lildinosaur"]
DEPENDENCIES = ["i2c"]
AUTO_LOAD = ["sensor", "text_sensor"]
MULTI_CONF = True

CONF_BME688_BSEC_ID = "bme688_bsec2_id"
CONF_IAQ_MODE = "iaq_mode"
CONF_SAMPLE_RATE = "sample_rate"
CONF_STATE_SAVE_INTERVAL = "state_save_interval"
CONF_BSEC_CONFIGURATION = "bsec_configuration"
CONF_TEMPERATURE_OFFSET = "temperature_offset"

bme688_bsec2_ns = cg.esphome_ns.namespace("bme688_bsec2")

IAQMode = bme688_bsec2_ns.enum("IAQMode")
IAQ_MODE_OPTIONS = {
    "STATIC": IAQMode.IAQ_MODE_STATIC,
    "MOBILE": IAQMode.IAQ_MODE_MOBILE,
}

SampleRate = bme688_bsec2_ns.enum("SampleRate")
SAMPLE_RATE_OPTIONS = {
    "LP": SampleRate.SAMPLE_RATE_LP,
    "ULP": SampleRate.SAMPLE_RATE_ULP,
}

BME688BSECComponent = bme688_bsec2_ns.class_(
    "BME688BSECComponent", cg.Component, i2c.I2CDevice
)

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(BME688BSECComponent),
        cv.Optional(CONF_TEMPERATURE_OFFSET, default=0): cv.temperature,
        cv.Optional(CONF_SAMPLE_RATE, default="LP"): cv.enum(
            SAMPLE_RATE_OPTIONS, upper=True
        ),
        cv.Optional(
            CONF_STATE_SAVE_INTERVAL, default="6hours"
        ): cv.positive_time_period_minutes,
        cv.Optional(CONF_BSEC_CONFIGURATION, default=""): cv.string,
    },
    cv.only_with_arduino,
    cv.Any(
        cv.only_on_esp8266,
        cv.All(
            cv.only_on_esp32,
            esp32.only_on_variant(supported=[esp32.const.VARIANT_ESP32]),
        ),
    ),
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await i2c.register_i2c_device(var, config)

    cg.add(var.set_temperature_offset(config[CONF_TEMPERATURE_OFFSET]))
    cg.add(var.set_sample_rate(config[CONF_SAMPLE_RATE]))
    cg.add(
        var.set_state_save_interval(config[CONF_STATE_SAVE_INTERVAL].total_milliseconds)
    )
    if config[CONF_BSEC_CONFIGURATION] != "":
        # Convert BSEC Config to int array
        temp = [int(a) for a in config[CONF_BSEC_CONFIGURATION].split(",")]
        # We can't call set_config_() with this array directly, because we don't
        # have a pointer in this case.
        # Instead we use a define, and handle it .cpp
        cg.add_define("bme688_bsec2_CONFIGURATION", temp)

    # Although this component does not use SPI, the BSEC library requires the SPI library
    cg.add_library("SPI", None)

    cg.add_define("USE_BSEC2")
    cg.add_library(
        "BME68x Sensor library",
        "1.1.40407",
        "https://github.com/BoschSensortec/Bosch-BME68x-Library.git",
    )
    cg.add_library(
        "BSEC2 Software Library",
        "1.6.2400",
        "https://github.com/boschsensortec/Bosch-BSEC2-Library.git",
    )
