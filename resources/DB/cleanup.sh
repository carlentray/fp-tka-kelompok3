#!/bin/bash
echo "Menghapus data orders dari load testing..."
sudo docker exec mongodb-server mongosh orderdb --eval "
db.orders.deleteMany({ created_at: { \$gt: new Date('2026-06-17') } });
print('Orders dihapus: ' + db.orders.countDocuments());
"
echo "Cleanup selesai!"
