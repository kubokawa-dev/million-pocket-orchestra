import { defineConfig } from 'orval';

export default defineConfig({
  main: {
    input: '../../packages/api-spec/tsp-output/@typespec/openapi3/openapi.yaml',
    output: {
      target: './src/api/client.ts',
      client: 'react-query',
      override: {
        mutator: {
          path: './src/api/axios-instance.ts',
          name: 'axiosInstance',
        },
      },
    },
  },
});
