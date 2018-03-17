#1
# Sets a default curve (secp256k1)
import random
from umbral import pre, keys, config

config.set_default_curve()

#2
# Generate keys for Alice and Bob
alice_priv_key = keys.UmbralPrivateKey.gen_key()
alice_pub_key = alice_priv_key.get_pubkey()

bob_priv_key = keys.UmbralPrivateKey.gen_key()
bob_pub_key = bob_priv_key.get_pubkey()

#3
# Encrypt some data for Alice
plaintext = b'Proxy Re-encryption is cool!!'
alice_ciphertext, umbral_capsule = pre.encrypt(alice_pub_key, plaintext)
print(alice_ciphertext)

#4
# Decrypt data for Alice
alice_decrypted_data = pre.decrypt(umbral_capsule, alice_priv_key, alice_ciphertext, alice_pub_key)
print(alice_decrypted_data)

#5
# Bob receives a capsule through a side channel (s3, ipfs, Google cloud, etc)
bob_capsule = umbral_capsule

#6
# Attempt Bob's decryption (fail)
try:
    fail_decrypted_data = pre.decrypt(bob_capsule, bob_priv_key, alice_ciphertext, alice_pubkey)
except:
    print("Decryption failed!")

#7
# Generate threshold split re-encryption keys via Shamir's Secret Sharing
# Use Alice's private key, and Bob's public key.
# Use a minimum threshold of 10, and create 20 total shares
kfrags = pre.split_rekey(alice_priv_key, bob_pub_key, 10, 20)

#8
# Have Ursula perform re-encrypton.
# Pick 10 random shares:
rand_min_shares = random.sample(kfrags, 10)

# Have Ursula re-encrypt the shares and attach them to the capsule:
for kfrag in rand_min_shares:
    cfrag = pre.reencrypt(kfrag, umbral_capsule)
    bob_capsule.attach_cfrag(cfrag)

#9
# Bob reconstructs the capsule and decrypts the ciphertext:
bob_plaintext = pre.decrypt(bob_capsule, bob_priv_key, alice_ciphertext, alice_pub_key)
print(bob_plaintext)
