def build_efficientnet(num_classes=NUM_CLASSES, img_size=CFG.IMG_SIZE):
    """EfficientNetB3 backbone + classifier head. Expects [0,255] inputs."""
    base = keras.applications.EfficientNetB3(
        include_top=False, weights="imagenet",
        input_shape=(img_size, img_size, 3), pooling="max")
    base.trainable = False                       # stage 1: head only

    inputs = keras.Input(shape=(img_size, img_size, 3), name="image_uint8_range")
    x = base(inputs, training=False)             # keeps BatchNorm in inference mode
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation="softmax", dtype="float32", name="predictions")(x)
    return keras.Model(inputs, outputs, name="efficientnetb3"), base

if CFG.TRAIN_EFFICIENTNET:
    effnet, backbone = build_efficientnet()
    effnet.compile(optimizer=keras.optimizers.Adamax(learning_rate=CFG.LR_HEAD),
                   loss=keras.losses.CategoricalCrossentropy(label_smoothing=CFG.LABEL_SMOOTHING),
                   metrics=METRICS)
    print(f"Backbone layers: {len(backbone.layers)} | "
          f"trainable params (stage 1): {sum(np.prod(v.shape) for v in effnet.trainable_weights):,}")
    effnet.summary()

# --- Stage 2: fine-tuning ---------------------------------------------------
backbone.trainable = True
for l in backbone.layers[:-CFG.FINETUNE_LAST_N]:
    l.trainable = False
for l in backbone.layers:                       # BatchNorm stays frozen while fine-tuning
    if isinstance(l, layers.BatchNormalization):
        l.trainable = False

effnet.compile(optimizer=keras.optimizers.Adamax(learning_rate=CFG.LR_FINETUNE),
               loss=keras.losses.CategoricalCrossentropy(label_smoothing=CFG.LABEL_SMOOTHING),
               metrics=METRICS)
