import json
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser()


parser.add_argument("--log_path", default=None, required=True, 
                    type=str, help="path to hydra_train.log")

args = parser.parse_args()

with open(args.log_path) as f:
    lines = f.readlines()

valid = []
train = []
for l in lines:
    info = l.strip().split(' - ')[-1]
    try:
        info = json.loads(info)
        if 'valid_loss' in info:
            valid.append(info)
        elif 'train_loss' in info:
            train.append(info)
    except:
        continue
        
train_loss = [float(t['train_loss']) for t in train]
valid_loss = [float(v['valid_loss']) for v in valid]
train_acc = [float(t['train_accuracy']) for t in train]
valid_acc = [float(v['valid_accuracy']) for v in valid]

print(f'T: {len(train)}')
print(f'V: {len(valid)}')
print(train_acc[-10:])
print(valid_acc[-10:])

fig, ((ax1), (ax2)) = plt.subplots(1, 2, figsize=[8,6]);
ax1.plot(train_loss,'r',linewidth=3.0)
ax1.plot(valid_loss,'b',linewidth=3.0)

ax1.set_xlabel('Epoch',fontsize=16)
ax1.set_ylabel('Loss',fontsize=16)
ax1.legend(['Train Loss', 'Valid Loss'],fontsize=18)

ax2.plot(train_acc,'r',linewidth=3.0)
ax2.plot(valid_acc,'b',linewidth=3.0)
ax2.set_xlabel('Epoch',fontsize=16)
ax2.set_ylabel('Accuracy',fontsize=16)
ax2.legend(['Train Acc', 'Valid Acc'],fontsize=18)

plt.title('wav2vec2.0',fontsize=16)
plt.savefig('pretrain.png')