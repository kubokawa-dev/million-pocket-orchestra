import { defineConfig } from 'orval';

export default defineConfig({
  'million-pocket': {
    input: {
      target: '../api-spec/tsp-output/@typespec/openapi3/openapi.yaml',
    },
    output: {
      mode: 'tags-split',
      target: './src/generated',
      client: 'react-query',
      httpClient: 'axios',
      baseUrl: '/api',
      mock: false,
      override: {
        mutator: {
          path: './src/axios-instance.ts',
          name: 'customAxiosInstance',
        },
        query: {
          useQuery: true,
          useMutation: true,
          signal: true,
        },
      },
    },
    hooks: {
      afterAllFilesWrite: 'prettier --write',
    },
  },
});
