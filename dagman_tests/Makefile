CXX=g++ -std=c++11
ROOT_FLAGS=`root-config --cflags --glibs`
CXX_OPTIONS= -O2 -std=c++11 -pedantic -Wall -Wextra
RAT_ROOT = $(RATROOT)
RAT_INC=$(RAT_ROOT)/include
RAT_EXTRN_INC=$(RAT_INC)/external
RAT_LIB_DIR=$(RAT_ROOT)/lib
RAT_LIB_NAME=RATEvent_Linux

SRC_FILES := $(wildcard src/*.cc *.cc  )
OBJ_FILES := $(addprefix build/, $(notdir $(SRC_FILES:.cc=.o)))

PREFIX ?= /usr/local/bin

INC_DIR=
LIB_DIR=lib
LIB_NAME=dagman_tests

LIB=$(LIB_DIR)/lib$(LIB_NAME).a

all: test1 test2

test1: test1.cc $(LIB)
	mkdir -p bin
	$(CXX) test1.cc $(INC_DIR) -I$(RAT_EXTRN_INC) -I$(RAT_INC) -w -L$(LIB_DIR) -L$(RAT_LIB_DIR) -l$(LIB_NAME) -l$(RAT_LIB_NAME) $(ROOT_FLAGS) -o $@

test2: test2.cc $(LIB)
	mkdir -p bin
	$(CXX) test2.cc $(INC_DIR) -I$(RAT_EXTRN_INC) -I$(RAT_INC) -w -L$(LIB_DIR) -L$(RAT_LIB_DIR) -l$(LIB_NAME) -l$(RAT_LIB_NAME) $(ROOT_FLAGS) -o $@

$(LIB) : $(OBJ_FILES)
	mkdir -p $(LIB_DIR)
	ar rcs  $@ $^

build/%.o : %.cc
	echo $(RAT_ROOT)
	mkdir -p build
	$(CXX) -c -w $< -I$(RAT_EXTRN_INC) -I$(RAT_INC) $(INC_DIR) -w $(ROOT_FLAGS) -o $@

install:
	ln -sf `readlink -f ./test1` $(PREFIX)
	chmod +x ./test1
	ln -sf `readlink -f ./test2` $(PREFIX)
	chmod +x ./test2

clean:
	rm -f test1
	rm -f test2
	rm -f build/*
	rm -f lib/*