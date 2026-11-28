import os
import json, urllib.request, uuid, random
S = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'sess.txt')).read().strip()
def call(a, args):
    r = urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8787/api', data=json.dumps({'action': a, 'args': args, 'session': S}).encode()))
    d = json.loads(r.read());
    if not d.get('ok'): print('ERR', a, d.get('error'))
    return d
cards = [('BCA All Cards', '2082', 'BCA', 'VISA', 50000000, 17, 6), ('BCA Tiket.com', '5912', 'BCA', 'MASTERCARD', 25000000, 20, 9),
         ('OCBC 90N', '7301', 'OCBC', 'VISA', 30000000, 12, 2), ('Mandiri Signature', '3174', 'Mandiri', 'VISA', 40000000, 25, 14),
         ('CIMB World', '1157', 'CIMB Niaga', 'MASTERCARD', 20000000, 5, 25)]
ids = []
for n, l4, bank, nw, lim, sd, dd in cards:
    d = call('api_saveCard', [str(uuid.uuid4()), {'Name': n, 'Last4': l4, 'Bank': bank, 'Network': nw, 'Credit_Limit': lim, 'Statement_Date': sd, 'Due_Date': dd, 'Status': 'Aktif', 'Holder_Name': 'HERMAWAN'}])
    ids.append(d['data']['card']['ID'] if 'data' in d else d.get('card', {}).get('ID'))
print(ids)
mer = ['Kopi Nako Grogol', 'TOKOPEDIA JAKARTA', 'SHOPEE ID', 'GRAB*FOOD', 'PERTAMINA SPBU 31', 'ALFAMART CILANDAK', 'GOOGLECLOUD5SwJ7G', 'Payment Other Bank Fee', 'TIKET.COM', 'STARBUCKS PIM', 'INDOMARET', 'NETFLIX.COM', 'ZUS COFFEE', 'HYPERMART', 'APOTEK K24']
random.seed(4)
for ci, cid in enumerate(ids[:4]):
    for m in ['2026-09', '2026-10']:
        rows = []
        tot = 0
        for i in range(8 + ci * 3):
            a = random.randint(2, 120) * 10000 if i % 5 else random.randint(15, 60) * 1000
            dte = f"{m}-{random.randint(1, 26):02d}"
            rows.append({'Date': dte, 'Booking_Date': dte, 'Merchant': random.choice(mer), 'Amount': a, 'Type': 'Belanja'})
            tot += a
        pd = m + '-%02d' % cards[ci][5]
        call('api_importStatement', [str(uuid.uuid4()), {'cardId': cid, 'bill': {'Print_Date': pd, 'Statement_Amount': tot, 'Minimum_Payment': round(tot * .1), 'Due_Date': '', 'Previous_Balance': 0}, 'rows': rows}])
# memo transaksi manual
for i in range(25):
    call('api_saveTransaction', [str(uuid.uuid4()), {'Date': f'2026-11-{random.randint(1, 22):02d}', 'Merchant': random.choice(mer), 'Amount': random.randint(2, 50) * 5000, 'Original_Currency': 'IDR', 'Card_ID': random.choice(ids), 'Kind': 'EXPENSE', 'Category_ID': 'C01', 'Source_Type': 'CC', 'Source_ID': random.choice(ids)}])
d = call('api_bootstrap', [1])
print(len(d['cards']), len(d['bills']), len(d['transactions']))
