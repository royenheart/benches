#include <omp.h>
#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

#define data_t unsigned long long

typedef struct Range Range;

struct Range {
    data_t start, end;
    Range(data_t s = 0, data_t e = 0) {
        start = s; end = e;
    }
};

data_t gen_A, gen_B, gen_C, n;
vector<data_t> arr;

data_t gen_next() {
    gen_A ^= gen_A << 31;
    gen_A ^= gen_A >> 17;
    gen_B ^= gen_B << 13;
    gen_B ^= gen_B >> 5;
    gen_A ^= gen_B;
    gen_B ^= ++gen_C;
    return gen_A;
}

// 使用递归的方法，当数值过大（不超过生成数据范围），会爆栈
// 需要注意每次调用时，右边界和左边界的取值，不要在超过数据范围内进行运算（对无符号数0减1）
void qs_seq(data_t l, data_t r) {
    if (l >= r) return;
    data_t mid = arr[r];
    data_t left = l, right = r - 1;
    while (left < right) {
        while (arr[left] < mid && left < right) left++;
        while (arr[right] >= mid && left < right) right--;
        swap(arr[left], arr[right]);
    }
    if (arr[left] >= arr[r]) {
        swap(arr[left], arr[r]);
    } else {
        left++;
    }
    qs_seq(l, left - 1);
    qs_seq(left + 1, r);
}

void qs_parallel(data_t l, data_t r) {
    if (l >= r) return;
    data_t mid = arr[r];
    data_t left = l, right = r - 1;
    
    #ifdef Debug
    printf("l:%llu r:%llu\n", l, r);
    #endif

    if (r - l < 8192) {
        auto i = arr.begin() + l;
        auto j = arr.begin() + r + 1;
        sort(i, j);
        return;
    }

    while (left < right) {
        while (arr[left] < mid && left < right) left++;
        while (arr[right] >= mid && left < right) right--;
        swap(arr[left], arr[right]);
    }
    if (arr[left] >= arr[r]) {
        swap(arr[left], arr[r]);
    } else {
        left++;
    }
    #pragma omp task
    {
        #ifdef Debug
        if (left < 1) {
            printf("left < 1, l: %llu, r: %llu, left: %llu\n", l, r, left);
            exit(EXIT_FAILURE);
        }
        #endif
        qs_parallel(l, left - 1);
    }
    #pragma omp task
    {
        qs_parallel(left + 1, r);
    }
}

void qs_parallel_root(data_t l, data_t r) {
    #pragma omp parallel num_threads(8)
    {
        #pragma omp single
        {
            qs_parallel(l, r);
        }
    }
}

void qs_iter_sort(data_t len) {
    if (len <= 0) return;
    Range *r = new Range[len];
    data_t p = 0;
    r[p++] = Range(0, len - 1);
    while (p) {
        Range range = r[--p];
        if (range.start >= range.end) continue;
        data_t mid = arr[range.end];
        data_t left = range.start, right = range.end - 1;
        while (left < right) {
            while (arr[left] < mid && left < right) left++;
            while (arr[right] >= mid && left < right) right--;
            swap(arr[left], arr[right]);
        }
        if (arr[left] >= arr[range.end]) {
            swap(arr[left], arr[range.end]);
        } else {
            left++;
        }
        r[p++] = Range(range.start, left - 1);
        r[p++] = Range(left + 1, range.end);
    }
}

// 串行冒泡排序
void sort_seq() {
    for (data_t i = 0, tmp; i < n; i++) {
        for (data_t j = 0; j < n - 1 - i; j++) {
            if (arr[j] > arr[j + 1]) {
                tmp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = tmp;
            }
        }
    }
}

// 升序排序并计算得到归一数
data_t get_res()
{
// 排序（如何选择更高效的排序算法）
#ifdef Debug
    double start_sort = omp_get_wtime();
#endif

    // qs_iter_sort(n);
    qs_parallel_root(0, n - 1);
    // qs_parallel(0, n - 1);
    // qs_seq(0, n - 1);
    // sort_seq();

#pragma omp taskwait

#ifdef Debug
    double end_sort = omp_get_wtime();
    cout << "Sort Time:" << end_sort - start_sort << endl;
#endif

// 计算归一数
#ifdef Debug
    double start_caln = omp_get_wtime();
#endif

    data_t res = 0;
    #pragma omp parallel for reduction(^ : res) num_threads(8)
    for (data_t i = 0; i < n; i++) {
        res ^= i * arr[i];
    }

#ifdef Debug
    double end_caln = omp_get_wtime();
    cout << "Calculate Out Time:" << end_caln - start_caln << endl;
#endif

    return res;
}

int main(int argc, char *argv[]) {
    omp_set_num_threads(8);

// 数据生成
#ifdef Debug
    double start_init = omp_get_wtime();
#endif

    #ifdef debug_in
    gen_A = (data_t)atoll(argv[1]);
    gen_B = (data_t)atoll(argv[2]);
    gen_C = (data_t)atoll(argv[3]);
    n = (data_t)atoll(argv[4]);
    #else
    cin >> gen_A >> gen_B >> gen_C >> n;
    #endif
    for (data_t i = 0; i < n; i++) {
        arr.push_back(gen_next());
    }

#ifdef Debug
    double end_init = omp_get_wtime();
    cout << "Init data Time:" << end_init - start_init << endl;
#endif

    data_t res = get_res();

    cout << res;
}

#undef data_t