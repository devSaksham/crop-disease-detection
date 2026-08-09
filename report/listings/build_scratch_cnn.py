def build_scratch_cnn(num_classes=NUM_CLASSES, img_size=CFG.IMG_SIZE):
    """VGG-style CNN, rebuilt functionally with in-graph rescaling."""
    inputs = keras.Input(shape=(img_size, img_size, 3), name="image_uint8_range")
    x = layers.Rescaling(1.0 / 255, name="rescale")(inputs)

    for filters in [64, 128, 128, 256, 512, 512]:
        x = layers.Conv2D(filters, 3, padding="same", activation="relu")(x)
        x = layers.Conv2D(filters, 3, padding="same", activation="relu")(x)
        x = layers.BatchNormalization()(x)
        x = layers.MaxPooling2D(2)(x)

    x = layers.Flatten()(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dense(64, activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation="softmax", dtype="float32", name="predictions")(x)
    return keras.Model(inputs, outputs, name="scratch_cnn")

cnn = build_scratch_cnn()
cnn.compile(optimizer=keras.optimizers.Adamax(learning_rate=CFG.LR_SCRATCH),
            loss=keras.losses.CategoricalCrossentropy(label_smoothing=CFG.LABEL_SMOOTHING),
            metrics=METRICS)
cnn.summary()
print(f"\nTrainable parameters: {cnn.count_params():,}")
