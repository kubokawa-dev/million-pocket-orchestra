import Axios, { AxiosRequestConfig } from 'axios';

// HonoサーバーのURL
const API_URL = 'http://localhost:8787';

export const AXIOS_INSTANCE = Axios.create({ baseURL: API_URL });

// Orvalが期待するミューテーター関数
export const axiosInstance = <T>(
  config: AxiosRequestConfig,
  options?: AxiosRequestConfig,
): Promise<T> => {
  const source = Axios.CancelToken.source();
  const promise = AXIOS_INSTANCE({
    ...config,
    ...options,
    cancelToken: source.token,
  }).then(({ data }) => data);

  // @ts-ignore
  promise.cancel = () => {
    source.cancel('Query was cancelled');
  };

  return promise;
};

export default axiosInstance;
