CXX ?= g++

FLAGS_ALWAYS = -std=c++20 -g -pipe -pthread -fvisibility=hidden -fcoroutines -fPIC -Wall -Wno-unused-function -Wno-unused-private-field -I$(TO_ROOT)/include/ -I$(TO_ROOT)/third-party/ $$(python3.7 -m pybind11 --includes) -DCATCH_CONFIG_MAIN -DFMT_HEADER_ONLY

FLAGS = $(FLAGS_ALWAYS)

default: test

test-%: %.cpp ../third-party/Catch2/single_include/catch2/catch.hpp
	$(CXX) $(FLAGS) $< -o $@.out $$(python3.7-config --ldflags)
	# execute test
	./$@.out

cov-%: %.cpp ../third-party/Catch2/single_include/catch2/catch.hpp
	$(CXX) $(FLAGS) $< -o $@.out
	#echo "running $@.out"
	# execute test
	./$@.out
	llvm-profdata merge default.profraw -o default.profdata
	llvm-cov show ./$@.out -instr-profile=default.profdata > coverage_$@.txt
	python $(TO_ROOT)/third-party/force-cover/fix_coverage.py coverage_$@.txt

# Test in debug mode without pointer tracker
test: $(addprefix test-, $(TEST_NAMES))
	rm -rf test*.out

# Test optimized version without debug features
opt: FLAGS := $(FLAGS_ALWAYS) -DNDEBUG -O3 -ffast-math -flto -march=native
opt: $(addprefix test-, $(TEST_NAMES))
	rm -rf test*.out

$(TO_ROOT)/coverage_include:
	./$(TO_ROOT)/test_include/convert_for_tests.sh

../third-party/Catch2/single_include/catch2/catch.hpp:
	git submodule init
	git submodule update

coverage: FLAGS := -$(FLAGS_ALWAYS) -Wnon-virtual-dtor -Wcast-align -Woverloaded-virtual -ftemplate-backtrace-limit=0 -fprofile-instr-generate -fcoverage-mapping -fno-inline -fno-elide-constructors -O0
coverage: $(TO_ROOT)/coverage_include $(addprefix cov-, $(TEST_NAMES))

clean:
	rm -f *.out
	rm -f *.o
	rm -f *.gcda
	rm -f *.gcno
	rm -f *.info
	rm -f *.gcov
	rm -f ./Coverage*
	rm -rf ./temp
