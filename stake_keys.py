
def load_keys(path):
  keys = []
  with open(path) as f:
      line = f.readline()
      while line:
          keys.append(line.replace('\n', ''))
          line = f.readline()
  return keys