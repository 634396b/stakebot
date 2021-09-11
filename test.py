import hmac

import hashlib


client_seed = '1'
server_seed = '2'

def plinko_result(nonce, client_seed, server_seed):
  message1 = '{}:{}:{}'.format(client_seed, nonce, 0)
  message2 = '{}:{}:{}'.format(client_seed, nonce, 1)
  message3 = '{}:{}:{}'.format(client_seed, nonce, 2)

  signature1 = hmac.new(bytes(server_seed , 'latin-1'), msg = bytes(message1 , 'latin-1'), digestmod = hashlib.sha256).hexdigest().upper()
  signature2 = hmac.new(bytes(server_seed , 'latin-1'), msg = bytes(message2 , 'latin-1'), digestmod = hashlib.sha256).hexdigest().upper()
  signature3 = hmac.new(bytes(server_seed , 'latin-1'), msg = bytes(message3 , 'latin-1'), digestmod = hashlib.sha256).hexdigest().upper()

  rows = 2*4*16
  sig = signature1 + signature2 + signature3
  totals = []
  for i in range(0, rows, 2 * 4):
    n1 = int(sig[i] + sig[i+1], 16)
    n2 = int(sig[i+2] + sig[i+3], 16)
    n3 = int(sig[i+4] + sig[i+5], 16)
    n4 = int(sig[i+6] + sig[i+7], 16)
    r = n1/(256**1) + n2/(256**2) + n3/(256**3) + n4/(256**4)
    r *= 2
    r = int(r)
    totals += [r]

  mp = {0: 1000, 1: 130, 2: 26, 3:9, 4:4, 5:2, 6:.2, 7:.2,8:.2, 9:.2, 10:.2, 11:2, 12: 4, 13:9, 14:26, 15:130, 16:1000}
  return mp[sum(totals)]

for i in range(100000):
  r = plinko_result(i, client_seed, server_seed)
  if r == 1000:
    print(i)