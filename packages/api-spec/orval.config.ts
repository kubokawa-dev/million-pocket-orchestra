import { defineConfig } from 'orval';

export default defineConfig({
  millionPocket: {
    input: './tsp-output/openapi.generated.yaml',
    output: {
      mode: 'tags-split',
      target: '../../apps/customer-mobile/api/generated/endpoints.ts',
      schemas: '../../apps/customer-mobile/api/generated/models',
      client: 'react-query',
      mock: false,
      clean: true,
      prettier: true,
      override: {
        mutator: {
          path: '../../apps/customer-mobile/api/axios-instance.ts',
          name: 'axiosInstance',
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
