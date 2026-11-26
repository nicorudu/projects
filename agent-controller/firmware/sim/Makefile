# Desktop simulator for the dock's screens: the same AgentUI library the dock compiles,
# in an SDL window on the Mac.
#
#   make            build ./build/agent-sim
#   make snapshots  render every screen in fixtures/screens.jsonl to PNG files in ./snapshots
#   make clean
#
# Run it through the bridge so the companion app drives it:  python ../../tools/sim_bridge.py
#
# LVGL and ArduinoJson come from the Arduino libraries folder (arduino-cli lib install lvgl
# ArduinoJson), so the simulator and the dock always use the same copies.
# Run make from this folder; the paths below are relative because the repo path has spaces.

ARDUINO_LIBS ?= $(HOME)/Documents/Arduino/libraries
LVGL ?= $(ARDUINO_LIBS)/lvgl
ARDUINOJSON ?= $(ARDUINO_LIBS)/ArduinoJson
UI := ../lib/AgentUI/src
BUILD := build

SDL_CFLAGS := $(shell sdl2-config --cflags) -I$(shell sdl2-config --prefix)/include
SDL_LIBS := $(shell sdl2-config --libs)

INCLUDES := -I$(UI) -I$(LVGL) -I$(ARDUINOJSON)/src $(SDL_CFLAGS)
CFLAGS := -O2 -g -std=c11 -w $(INCLUDES)
CXXFLAGS := -O2 -g -std=c++17 -Wall -Wextra $(INCLUDES)

LVGL_SRC := $(shell find $(LVGL)/src -name '*.c')
LVGL_OBJ := $(patsubst $(LVGL)/src/%.c,$(BUILD)/lvgl/%.o,$(LVGL_SRC))
UI_OBJ := $(BUILD)/ui/AgentUI.o $(BUILD)/ui/ui_text.o
SIM_OBJ := $(BUILD)/main.o

.PHONY: all snapshots clean
all: $(BUILD)/agent-sim

$(BUILD)/agent-sim: $(LVGL_OBJ) $(UI_OBJ) $(SIM_OBJ)
	$(CXX) -o $@ $^ $(SDL_LIBS) -lpthread

$(BUILD)/lvgl/%.o: $(LVGL)/src/%.c $(UI)/lv_conf.h
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/ui/%.o: $(UI)/%.cpp $(wildcard $(UI)/*.h)
	@mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) -c $< -o $@

$(BUILD)/main.o: main.cpp $(wildcard $(UI)/*.h)
	@mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) -c $< -o $@

snapshots: $(BUILD)/agent-sim
	@rm -rf snapshots && mkdir -p snapshots
	$(BUILD)/agent-sim --script fixtures/screens.jsonl --out snapshots
	@for f in snapshots/*.bmp; do sips -s format png "$$f" --out "$${f%.bmp}.png" >/dev/null && rm "$$f"; done
	@ls snapshots

clean:
	rm -rf $(BUILD) snapshots
