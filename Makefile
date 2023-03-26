TARGET := main$(shell python3-config --extension-suffix)
CXXFLAGS := -O3 --std=c++20 -Iinclude -Iinclude/pybind11/include $(shell python3-config --includes)

include config.mk

SRCS := $(shell find src/lib -name '*.cpp')

OBJS := $(addsuffix .o,$(addprefix build/lib/, $(notdir $(SRCS))))
build/lib/$(TARGET): $(OBJS)
	mkdir -p build
	mkdir -p build/lib
	$(CXX) -shared -fPIC -o $@ $^

build/lib/%.cpp.o: src/lib/%.cpp
	mkdir -p build
	mkdir -p build/lib
	$(CXX) -c $(CXXFLAGS) -o $@ $< 

.PHONY: clean
clean:
	rm -rf build
