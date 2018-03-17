==============
Using pyUmbral
==============
.. image:: .static/PRE_image.png


Import umbral modules

.. code-block:: python

  from umbral import pre, keys, config


Configuration
==============


Setting the default curve
--------------------------

The best way to start using pyUmbral is to decide on a elliptic curve to use and set it as your default.

.. code-block:: python

    config.set_default_curve(ec.SECP256K1)

For more information on curves, see :doc:`choosing_and_using_curves`.


Encryption and Encapsulation
=============================


Generate an Umbral key pair
-----------------------------
First, Let's generate an asymmetric key pair for Alice.

.. code-block:: python

  alices_private_key = keys.UmbralPrivateKey.gen_key()
  alices_public_key = private_key.get_pubkey()


Encrypt with a public key
--------------------------
Now let's encrypt data with Alice's public key.
Invocation of `umbral.encrypt` returns both the `ciphertext`,
and a `capsule`, Anyone with Alice's public key can perform
this operation.

.. code-block:: python

  plaintext = b'Proxy Re-encryption is cool!'
  ciphertext, capsule = umbral.encrypt(alices_public_key,
                                       plaintext)


Decrypt with a private key
---------------------------
Since data was encrypted with Alice's public key,
Alice can open the capsule and decrypt the ciphertext with her private key.

.. code-block:: python

    cleartext = umbral.decrypt(capsule, alices_private_key,
                               ciphertext, alices_public_key)


Threshold split-key re-encryption
==================================


Alice grants access to Bob by generating kfrags 
-----------------------------------------------
When Alice wants to grant Bob access to open her encrypted messages, 
she creates *threshold split re-encryption keys*, or *"kfrags"*, 
which are next sent to N proxies or *Ursulas*. 

| Generate re-encryption key fragments with "`M` of `N`":
| `M` - Minimum threshold of key fragments needed to activate a capsule.
| `N` - Total number of key fragments to generate.

.. code-block:: python

   kfrags = umbral.split_rekey(alices_private_key,
                                  bobs_public_key,
                                  10,    # M - Threshold
                                  20)    # N - Total


Bob receives a capsule
-----------------------
Next, let's generate a key pair for Bob, and pretend to send
him the capsule through a side channel like
S3, IPFS, Google Cloud, Sneakernet, etc.

.. code-block:: python

   # Generate a key pair for Bob
   bobs_private_key = keys.UmbralPrivateKey.gen_key()
   bobs_public_key = private_key.get_pubkey()

   # Bob receives the capsule
   capsule = <fetch a capsule through side channel>


Bob fails to open the capsule
-------------------------------
If Bob attempts to open a capsule that was not encrypted for his public key,
or re-encrypted for him by Ursula, he will not be able to open it.

.. code-block:: python

  try:
      fail = umbral.decrypt(capsule,
                            bobs_private_key,
                            ciphertext,
                            alices_public_key)
  except:
      print("Decryption failed!")


Ursulas perform re-encryption
------------------------------
Bob asks several Ursulas to re-encrypt the capsule so he can open it. 
Each Ursula performs re-encryption on the capsule using the `kfrag` 
provided by Alice, obtaining this way a "capsule fragment", or `cfrag`,
Let's mock a network or transport layer by sampling `M` random `kfrags`,
one for each required Ursula.

Bob collects the resulting `cfrags` from several Ursulas. 
Bob must gather at least `M` `cfrags` in order to activate the capsule.


.. code-block:: python

  import random

  kfrags = random.sample(kfrags,    # All kfrags from above
                         10)        # M - Threshold

  cfrags = list()             # Bob's cfrag collection
  for kfrag in kfrags:
      cfrag = umbral.reencrypt(kfrag, capsule)
      cfrags.append(cfrag)    # Bob collects a cfrag


Bob attaches cfrags to the capsule
----------------------------------
Bob attaches at least `M` `cfrags` to the capsule;
Then it can become *activated*.

.. code-block:: python

   for cfrag in cfrags:
       capsule.attach_cfrag(cfrag)


Bob activates and opens the capsule
------------------------------------
Finally, Bob activates and opens the capsule,
then decrypts the re-encrypted ciphertext.

.. code-block:: python

   cleartext = umbral.decrypt(capsule, bobs_private_key,
                              ciphertext, alices_public_key)
