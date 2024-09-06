from pylabel import importer
import os
import shutil

ds = importer.ImportVOC("New dataset_VOC/train/Annotations","New dataset_VOC/train/Images")

ds.splitter.GroupShuffleSplit(train_pct=.85, val_pct=.1, test_pct=.05)

val_files = sorted(ds.df[ds.df['split'] == 'val']['img_filename'])
test_files = sorted(ds.df[ds.df['split'] == 'test']['img_filename'])
for p in val_files:
    #p = p.replace('\\','/')
    nfp = os.path.join('New dataset_VOC/val/images/',p)
    fp = os.path.join('New dataset_VOC/train/images/',p)
    
    label_p = p.replace('.png','.xml')
    label_p = label_p.replace('.jpeg','.xml')
    label_nfp = os.path.join('New dataset_VOC/val/annotations/',label_p)
    label_fp = os.path.join('New dataset_VOC/train/annotations/',label_p)

    shutil.move(fp,nfp)
    shutil.move(label_fp,label_nfp)
for p in test_files:
    #p = p.replace('\\','/')
    nfp = os.path.join('New dataset_VOC/test/images',p)
    fp = os.path.join('New dataset_VOC/train/images',p)
    
    label_p = p.replace('.png','.xml')
    label_p = label_p.replace('.jpeg','.xml')
    label_nfp = os.path.join('New dataset_VOC/test/annotations/',label_p)
    label_fp = os.path.join('New dataset_VOC/train/annotations/',label_p)

    shutil.move(fp,nfp)
    shutil.move(label_fp,label_nfp)



