# ----------------------------- CONFIGURATION -----------------------------
class CFG:
    # data
    KAGGLE_DATASET   = "emmarex/plantdisease"
    IMG_SIZE         = 224          # EfficientNetB3 native is 300; 224 keeps it light
    BATCH_SIZE       = 32
    VAL_FRAC         = 0.15
    TEST_FRAC        = 0.15
    SEED             = 42
    VERIFY_IMAGES    = True         # scan every file with PIL for corruption

    # training
    TRAIN_SCRATCH_CNN = True        # Model A (the hand-built CNN)
    TRAIN_EFFICIENTNET = True       # Model B (EfficientNetB3)
    EPOCHS_SCRATCH   = 30
    EPOCHS_HEAD      = 8            # EfficientNet, frozen backbone
    EPOCHS_FINETUNE  = 7            # EfficientNet, unfrozen top blocks
    LR_SCRATCH       = 1e-3
    LR_HEAD          = 1e-3
    LR_FINETUNE      = 1e-5
    FINETUNE_LAST_N  = 60           # trainable layers from the top of the backbone
    PATIENCE         = 6
    USE_CLASS_WEIGHTS = True
    LABEL_SMOOTHING  = 0.05

    # quick smoke test
    QUICK_RUN        = False
    QUICK_PER_CLASS  = 60
    QUICK_EPOCHS     = 2

    # output
    OUT_DIR          = Path("artifacts")

CFG.OUT_DIR.mkdir(parents=True, exist_ok=True)
(CFG.OUT_DIR / "figures").mkdir(exist_ok=True)
(CFG.OUT_DIR / "models").mkdir(exist_ok=True)
(CFG.OUT_DIR / "logs").mkdir(exist_ok=True)

if CFG.QUICK_RUN:
    CFG.EPOCHS_SCRATCH = CFG.EPOCHS_HEAD = CFG.EPOCHS_FINETUNE = CFG.QUICK_EPOCHS
    print("QUICK_RUN enabled -- subsampled data, 2 epochs per stage. Results are NOT representative.")
