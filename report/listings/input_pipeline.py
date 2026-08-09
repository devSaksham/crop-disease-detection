_aug_layers = [
    layers.RandomFlip("horizontal_and_vertical", seed=CFG.SEED),
    layers.RandomRotation(0.06, fill_mode="reflect", seed=CFG.SEED),   # about +/-20 degrees
    layers.RandomZoom(0.15, fill_mode="reflect", seed=CFG.SEED),
    layers.RandomTranslation(0.08, 0.08, fill_mode="reflect", seed=CFG.SEED),
    layers.RandomContrast(0.15, seed=CFG.SEED),
]
try:                                                                   # TF >= 2.9
    _aug_layers.append(layers.RandomBrightness(0.10, value_range=(0, 255), seed=CFG.SEED))
except Exception:
    pass
augmenter = keras.Sequential(_aug_layers, name="augmenter")

def _load(path, label):
    img = tf.io.read_file(path)
    img = tf.io.decode_image(img, channels=3, expand_animations=False)
    img.set_shape([None, None, 3])
    img = tf.image.resize(img, (CFG.IMG_SIZE, CFG.IMG_SIZE), method="bilinear")
    img = tf.cast(img, tf.float32)                                     # stays in [0, 255]
    return img, tf.one_hot(label, NUM_CLASSES)

def make_dataset(frame, training=False, augment=False, batch=None):
    batch = batch or CFG.BATCH_SIZE
    ds = tf.data.Dataset.from_tensor_slices(
        (frame.filepath.values, frame.label_idx.values.astype(np.int32)))
    if training:
        ds = ds.shuffle(min(len(frame), 8192), seed=CFG.SEED, reshuffle_each_iteration=True)
    ds = ds.map(_load, num_parallel_calls=AUTOTUNE).batch(batch)
    if augment:
        ds = ds.map(lambda x, y: (augmenter(x, training=True), y), num_parallel_calls=AUTOTUNE)
    return ds.prefetch(AUTOTUNE)

train_ds = make_dataset(train_df, training=True,  augment=True)
val_ds   = make_dataset(val_df,   training=False, augment=False)   # deterministic, order-locked
test_ds  = make_dataset(test_df,  training=False, augment=False)   # deterministic, order-locked
