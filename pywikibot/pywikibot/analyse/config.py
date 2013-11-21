class Classification:
    GOOD = 1
    BAD = 2

TRAINING_DATA_FILE = "clf.pkl"

TRAIN_DATA = [(u"Reform", Classification.BAD),
              (u"Füsiokraadid", Classification.GOOD),
              (u"Oru vald (1939)", Classification.BAD)]