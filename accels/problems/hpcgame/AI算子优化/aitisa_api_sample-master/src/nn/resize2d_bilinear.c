#include "resize2d_bilinear.h"
#include "src/core/dispatch.h"
#include "math.h"
#define resize2d_bilinear_kernel(typename)                                 \
  typename* in_data = aitisa_tensor_data(input);                           \
  typename* out_data = aitisa_tensor_data(*output);                        \
  for (int64_t i = 0; i < target_h; i++) {                                 \
    for (int64_t j = 0; j < target_w; j++) {                               \
      double raw_u = i * (double)h / (double)target_h;                     \
      double raw_v = j * (double)w / (double)target_w;                     \
      int64_t u = (int64_t)raw_u;                                          \
      int64_t v = (int64_t)raw_v;                                          \
      if (u + 1 == h || v + 1 == w) {                                      \
        out_data[i * target_w + j] = in_data[u * w + v];                   \
        continue;                                                          \
      }                                                                    \
      typename f00 = in_data[u * w + v];                                   \
      typename f01 = in_data[u * w + v + 1];                               \
      typename f10 = in_data[(u + 1) * w + v];                             \
      typename f11 = in_data[(u + 1) * w + v + 1];                         \
      double x = raw_u - u;                                                \
      double y = raw_v - v;                                                \
      out_data[i * target_w + j] = f00 * (1 - x) * (1 - y) +               \
                                   f01 * (1 - x) * y + f10 * x * (1 - y) + \
                                   f11 * x * y;                            \
    }                                                                      \
  }

Status aitisa_resize2d_bilinear(const Tensor input, int target_h, int target_w,
                                Tensor* output) {
  int64_t* dims = aitisa_tensor_dims(input);
  int64_t ndim = aitisa_tensor_ndim(input);
  Status status = STATUS_SUCCESS;
  DataType dtype = aitisa_tensor_data_type(input);
  switch (dtype.code) {
    case TYPE_FLOAT:
      break;
    case TYPE_DOUBLE:
      break;
    default:
      return STATUS_NOT_SUPPORTED;
  }
  if (ndim == 2)  // [H, W]
  {
    int h = dims[0];
    int w = dims[1];

    int64_t output_dims[2] = {target_h, target_w};

    Tensor new_tensor;
    DataType dtype = aitisa_tensor_data_type(input);
    Device device = aitisa_tensor_device(input);

    CHECK_STATUS(
        aitisa_create(dtype, device, output_dims, ndim, NULL, 0, &new_tensor));
    *output = new_tensor;
    int64_t size = aitisa_tensor_size(input);
    AITISA_DISPATCH_ALL_TYPES_RETURN(dtype, resize2d_bilinear_kernel);
  } else {
    status = STATUS_TYPE_MISMATCH;
  }
  return status;
}
