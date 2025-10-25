import sys
sys.path.insert(0, 'c:/Users/kubok/Develop/projects/million-pocket')
from tools.utils import load_all_loto6_draws

df = load_all_loto6_draws()
print('Columns:', df.columns.tolist())
print('\nSample data:')
print(df.head(2))
print('\nData shape:', df.shape)
