import os
import shutil
import unittest
import io
import contextlib
from backup import backup_and_compress

class TestBackup(unittest.TestCase):
    def setUp(self):
        self.source = "test_data/source"
        self.dest = "test_data/destination"
        os.makedirs(self.source, exist_ok=True)
        os.makedirs(self.dest, exist_ok=True)
        with open(os.path.join(self.source, "test.txt"), "w") as f:
            f.write("Hello Backup")

    def tearDown(self):
        shutil.rmtree("test_data")

    def test_backup_creates_zip(self):
        # Rediriger les sorties pour éviter le bruit
        with io.StringIO() as buf, contextlib.redirect_stdout(buf):
            backup_and_compress(self.source, self.dest)
        zip_files = [f for f in os.listdir(self.dest) if f.endswith(".zip")]
        self.assertGreater(len(zip_files), 0)

if __name__ == '__main__':
    unittest.main()
