# Naive CUDA GEMM for Nsight Systems practice
NVCC      ?= nvcc
ARCH      ?= native
N         ?= 1024
ITERS     ?= 10
TARGET    := gemm
SRC       := gemm.cu
NSYS_OUT  := gemm_report

NVCCFLAGS := -O3 -std=c++17 -arch=$(ARCH)

.PHONY: all clean run profile help

all: $(TARGET)

$(TARGET): $(SRC)
	$(NVCC) $(NVCCFLAGS) -o $@ $<

run: $(TARGET)
	./$(TARGET) $(N) $(ITERS)

profile: $(TARGET)
	nsys profile -o $(NSYS_OUT) -f true --stats=true \
		--trace=cuda,nvtx,osrt \
		./$(TARGET) $(N) $(ITERS)
	@echo "Report: $(NSYS_OUT).nsys-rep"
	@echo "Open with: nsys-ui $(NSYS_OUT).nsys-rep"

clean:
	rm -f $(TARGET) $(TARGET).exe *.o *.obj \
		$(NSYS_OUT).nsys-rep $(NSYS_OUT).sqlite

help:
	@echo "make              # build gemm"
	@echo "make run N=1024 ITERS=10"
	@echo "make profile N=1024 ITERS=10"
	@echo "make clean"
	@echo "ARCH=sm_89 make   # override GPU arch"
