#include "src/math/matmul_simple.h"
#include "src/basic/broadcast.h"
#include "src/basic/factories.h"
#include "src/core/allocator.h"
#include "src/core/dispatch.h"
#include "src/core/utils.h"

// kernel of matrix-matrix multiply
#define MM_KERNEL_SIMPLE(typename, A, B, C, M, K, N)                         \
    for (int i = 0; i < M; ++i)                                              \
    {                                                                        \
        for (int j = 0; j < N; ++j)                                          \
        {                                                                    \
            for (int q = 0; q < K; ++q)                                      \
            {                                                                \
                ((typename *)C)[i * N + j] +=                                \
                    ((typename *)A)[i * K + q] * ((typename *)B)[q * N + j]; \
            }                                                                \
        }                                                                    \
    }

// choose mm kernel according to dtype.code
Status mm_simple_template(DataType dtype, void *A, void *B, void *C, int64_t M,
                          int64_t K, int64_t N)
{
    AITISA_DISPATCH_ALL_TYPES_RETURN(dtype, MM_KERNEL_SIMPLE, A, B, C, M, K,
                                     N);
    return STATUS_SUCCESS;
}

// Definition of aitisa_matmul.
Status aitisa_matmul_simple(const Tensor tensor1, const Tensor tensor2,
                            Tensor *output)
{
    if (aitisa_tensor_device(tensor1).type != DEVICE_CPU ||
        aitisa_tensor_device(tensor2).type != DEVICE_CPU)
    {
        return STATUS_NOT_SUPPORTED;
    }
    int64_t ndim_tensor1 = aitisa_tensor_ndim(tensor1);
    int64_t ndim_tensor2 = aitisa_tensor_ndim(tensor2);
    Status status = STATUS_SUCCESS;
    if (ndim_tensor1 == 2 && ndim_tensor2 == 2)
    {
        // matrix-matrix
        int64_t dim0_tensor1 = aitisa_tensor_dim(tensor1, 0);
        int64_t dim1_tensor1 = aitisa_tensor_dim(tensor1, 1);
        int64_t dim0_tensor2 = aitisa_tensor_dim(tensor2, 0);
        int64_t dim1_tensor2 = aitisa_tensor_dim(tensor2, 1);
        if (dim1_tensor1 != dim0_tensor2)
        {
            return STATUS_DIMENSIONS_MISMATCH;
        }
        // create output
        int64_t ndim_out = 2;
        int64_t dims_out[2] = {dim0_tensor1, dim1_tensor2};
        CHECK_STATUS(aitisa_full(aitisa_tensor_data_type(tensor1),
                                 aitisa_tensor_device(tensor1), dims_out, ndim_out,
                                 0.0, output));
        // call kernel
        CHECK_STATUS(mm_simple_template(
            aitisa_tensor_data_type(tensor1), aitisa_tensor_data(tensor1),
            aitisa_tensor_data(tensor2), aitisa_tensor_data(*output), dim0_tensor1,
            dim1_tensor1, dim1_tensor2));
    }
    else
    {
        status = STATUS_INVALID_ARGUMENT;
    }
    return status;
}
