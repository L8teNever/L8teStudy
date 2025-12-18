from pywebpush import Vapid

private_key = Vapid().generate_vapid_keys()
print("VAPID_PRIVATE_KEY=" + str(private_key[0].strip()))
print("VAPID_PUBLIC_KEY=" + str(private_key[1].strip()))
print("VAPID_CLAIMS_EMAIL=mailto:admin@l8testudy.app")
