
#include<iostream>
#include <locale>
#include <chrono>
#include "cuda.h"

#define OK(ans) { ok_assert((ans), __FILE__, __LINE__); }
inline void ok_assert(cudaError_t code, const char *file, int line, bool abort=true) {
   if (code != cudaSuccess) {
	   std::cerr<<"error: "<< cudaGetErrorString(code)<<", "<< file<<":"<< line <<'\n';
      if (abort) { std::exit(code); }
   }
}
 
struct SEP1K : std::numpunct<char> {
	char do_thousands_sep()   const { return ','; } 
	std::string do_grouping() const { return "\3"; }
};

cudaDeviceProp device_prop(int devid, int verbose) {
	cudaDeviceProp prop;
	int maxdev {0};
	OK( cudaGetDeviceCount(&maxdev) );
	if (devid >= maxdev) {
		std::cerr<<"fatal: invalid device (gpu) id selected.\n";
		std::exit(1);
	}
	OK( cudaSetDevice(devid) );
	OK( cudaGetDeviceProperties(&prop, devid) );
	if (verbose) {
		auto prev = std::cout.imbue(std::locale(std::cout.getloc(), new SEP1K));
		std::cout<<prop.name<<" [gpu: "<<devid<<"/"<<maxdev<<"], global mem="<<prop.totalGlobalMem<<'\n';
		std::cout.imbue(prev);
	}
	return prop;
}
void membench(float ratio, size_t sz) {
	// cudamalloc does not oversubscribe as for unified memory.
	size_t sz2 = ratio > .98 ? .98*sz/ratio : sz;
	void *h, *d;
	h = malloc(sz2);
	if (!h) std::exit(2);
	OK( cudaMalloc(&d, sz2) );
	OK( cudaMemcpy(d, h, sz2, cudaMemcpyHostToDevice) );
	OK( cudaMemcpy(h, d, sz2, cudaMemcpyDeviceToHost) );
}

__device__
unsigned int rand (unsigned int *rand_next) {
       *rand_next = *rand_next * 1103515245 + 12345; 
       return ((unsigned int)(*rand_next / 65536) % 32768);
}

__global__ void busy(int jmax, size_t n, float *data) {
	size_t tid = threadIdx.x + blockIdx.x * blockDim.x;
	size_t stride = gridDim.x * blockDim.x;
	for (size_t i=tid; i<n; i+=stride) {
		float x{0.};
		unsigned int rand_next=i;
		for (unsigned int j=0; j<jmax; ++j) {
			// idea is to have int and float operations (64 cores for each on 7.x)
			x += normcdfinvf(rand(&rand_next));
		}
		data[i] = x;
	}
}
void cpubench(int loop, size_t sz, int blk, int tpb, int verbose) {
	float *data;  // float: 7.x => 64 FP32 cores, 16 special cores.
	size_t n = sz/sizeof(*data);
	OK( cudaMallocManaged(&data, n*sizeof(*data)) );
	if (verbose) { 
		auto prev = std::cout.imbue(std::locale(std::cout.getloc(), new SEP1K));
		std::cout<<"mem="<<n*sizeof(*data)<<" B ["<<n<<" x "<<sizeof(*data)<<" B]\n";
		std::cout.imbue(prev);
	}
	busy<<<blk, tpb>>>(loop, n, data);
	OK( cudaPeekAtLastError() );
	OK( cudaDeviceSynchronize() );
	OK( cudaFree(data) );
}

int main(int argc, char *argv[]) {
	int verbose {1}; // default is verbose, -s (silent) removes output
	int rc {EXIT_SUCCESS};
	int bench {0}; // bench type
	float memratio {0.};
	size_t memsz {0};  // memory size
	int tpb {0}; // threads/block
	int blk {0}; // blocks
	int loop{0};
	int ia {1};
	int dev {0}; // target device id 
	if (argc >= 2) { 
		if (std::string(argv[ia]) == "-h")  {
			std::cout<<"arguments: bench [-s] device_id bench_id {0*: mem, 1: cpu} mem_ratio threads/block blocks loop\n"; 
			return EXIT_SUCCESS;
		} else if (std::string(argv[ia]) == "-s") {
			verbose = 0;
			++ia;
		}
	}
	if (ia < argc) { dev = std::stoi(argv[ia++]); }
	if (ia < argc) { bench = std::stoi(argv[ia++]); }
	if (ia < argc) { memratio = std::stof(argv[ia++]); }
	if (ia < argc) { tpb = std::stoi(argv[ia++]); }
	if (ia < argc) { blk = std::stoi(argv[ia++]); }
	if (ia < argc) { loop = std::stoi(argv[ia++]); }
	auto prop = device_prop(dev, verbose);
	if (memratio <= 0.) memratio = .25;
	memsz = prop.totalGlobalMem * memratio;
	if (tpb > prop.maxThreadsPerBlock || tpb <= 0) tpb = prop.maxThreadsPerBlock;
	if (blk <= 0) blk = 2*prop.multiProcessorCount;
	if (loop == 0) loop = 1000;
	if (verbose) {
		std::cout<<"bench "<<bench<<", mem="<<100.0*memratio<<"%, threads/block="<<tpb<<", blocks="<<blk<<'\n';
	}
	auto t0 = std::chrono::high_resolution_clock::now();
	if (bench == 0) membench(memratio, memsz);
	else cpubench(loop, memsz, blk, tpb, verbose); 
	auto t1 = std::chrono::high_resolution_clock::now();
        std::cout<< std::chrono::duration_cast<std::chrono::seconds>(t1-t0).count()<<'\n';

	return rc;
}
