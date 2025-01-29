import rsa

(bob_pub, bob_priv) = rsa.newkeys(512)

message = 'hello Bob!'.encode('utf8')
crypto = rsa.encrypt(message, bob_pub)
print(crypto)

message = rsa.decrypt(crypto, bob_priv)
print(message.decode('utf8'))