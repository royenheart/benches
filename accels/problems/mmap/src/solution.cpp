#include <omp.h>
#include <cstdio>
#include <cstdlib>
#include <sys/mman.h>
#include <unistd.h>
#include <sys/types.h>
#include <fcntl.h>

int main(int argc, char* argv[]) {
    int64_t out = 0;
    int fd, fw;
    fd = open("input.bin", O_RDONLY);
    int32_t *twoargs = (int32_t*)mmap(0, sizeof(int32_t) * 2, PROT_READ, MAP_PRIVATE, fd, 0);
    int32_t p = twoargs[0];
    int32_t n = twoargs[1];
    int32_t *array = (int32_t*)mmap(0, sizeof(int32_t) * (2 + n), PROT_READ, MAP_PRIVATE, fd, 0);

    omp_set_num_threads(p);
    #pragma omp parallel for reduction(+ : out) 
    for (unsigned long long i = 0; i < n; ++i) {
        out += array[i + 2];
    }
    out %= 100001651;
    int32_t out32 = (int32_t)out;

    #ifdef Debug
    printf("p: %d, n: %d, out: %d\n", p, n, out32);
    #endif

    // FILE* fp = NULL;
    // fp = fopen("output.bin", "wb");
    // fwrite((void*)&out32, sizeof(int32_t), 1, fp);
    // fwrite((void*)arr, sizeof(int32_t), n, fp);
    // fclose(fp);
    fw = open("output.bin", O_CREAT | O_RDWR, 0666);
    ftruncate(fw, sizeof(int32_t) * (n + 1));
    int32_t* wri = (int32_t*)mmap(0, sizeof(int32_t) * (n + 1), PROT_READ | PROT_WRITE, MAP_SHARED, fw, 0);
    wri[0] = out;
    for (unsigned long long i = 1; i <= n; i++) {
        wri[i] = array[i + 1] + 1;
    }

    munmap(twoargs, sizeof(int32_t) * 2);
    munmap(array, sizeof(int32_t) * (2 + n));
    close(fd); 
}