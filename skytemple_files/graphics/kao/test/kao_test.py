#  Copyright 2020-2021 Capypara and the SkyTemple Contributors
#
#  This file is part of SkyTemple.
#
#  SkyTemple is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SkyTemple is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SkyTemple.  If not, see <https://www.gnu.org/licenses/>.

from skytemple_files.graphics.kao.handler import KaoHandler
from skytemple_files.graphics.kao.protocol import KaoProtocol
from skytemple_files.test.case import SkyTempleFilesTestCase, fixpath

FIX_IN_TEST_MAP = {
    0: [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 32, 34],
    552: [0, 2, 4, 6, 8, 10],
    1153: []
}
FIX_IN_LEN = 1154
FIX_IN_LEN_SUB = 40


class KaoTestCase(SkyTempleFilesTestCase[KaoHandler, KaoProtocol]):
    handler = KaoHandler

    def setUp(self) -> None:
        self.kao = self._load_main_fixture(self._fix_path_kao())
        self.assertIsNotNone(self.kao)

    def test_get(self):
        for idx, sidxs in FIX_IN_TEST_MAP.items():
            for sidx in sidxs:
                kaoimg = self.kao.get(idx, sidx)
                self.assertGreater(kaoimg.size(), 0)
                # Kaos are not guaranteed to use the same exact palette after storing.
                self.assetImagesEqual(self._fix_path_png(idx, sidx), kaoimg.get(), rgb_diff=True)
                self.assetImagesEqual(self._fix_path_png(idx, sidx, rgb=True), kaoimg.get(), rgb_diff=True)

    def test_get_missing(self):
        self.assertIsNone(self.kao.get(552, 1))
        with self.assertRaises(ValueError):
            self.kao.get(0, FIX_IN_LEN_SUB)
        with self.assertRaises(ValueError):
            self.kao.get(FIX_IN_LEN, 0)

    def test_set_from_img(self):
        img = self._load_image(self._fix_path_png(0, 1))
        self.kao.set_from_img(552, 8, img)
        self.kao.set_from_img(1153, 4, img)
        new_kao = self._save_and_reload_main_fixture(self.kao)
        self.assetImagesNotEqual(img, new_kao.get(0, 2).get(), rgb_diff=True)
        self.assetImagesEqual(img, new_kao.get(552, 8).get(), rgb_diff=True)
        self.assetImagesNotEqual(img, new_kao.get(552, 4).get(), rgb_diff=True)
        self.assetImagesEqual(img, new_kao.get(1153, 4).get(), rgb_diff=True)
        self.assertIsNone(new_kao.get(1153, 0))

    def test_delete(self):
        img = self._load_image(self._fix_path_png(0, 1))
        self.kao.delete(552, 4)
        self.kao.delete(1232132, 432131)
        self.kao.delete(552, 1)
        new_kao = self._save_and_reload_main_fixture(self.kao)
        self.assertIsNotNone(new_kao.get(0, 2))
        self.assertIsNotNone(new_kao.get(552, 8))
        self.assertIsNone(new_kao.get(0, 1))
        self.assertIsNotNone(new_kao.get(552, 0))
        self.assertIsNone(new_kao.get(552, 1))
        self.assertIsNotNone(new_kao.get(552, 2))
        self.assertIsNone(new_kao.get(552, 4))
        self.assertIsNotNone(new_kao.get(552, 6))

    def test_expand(self):
        with self.assertRaises(ValueError):
            self.kao.get(2000, 0)
        self.kao.expand(2001)
        new_kao = self._save_and_reload_main_fixture(self.kao)
        with self.assertRaises(ValueError):
            new_kao.get(2001, 0)
        self.assertIsNone(new_kao.get(2000, 0))

    def test_raw(self):
        kaoimg = self.kao.get(0, 2)
        raw = kaoimg.raw()
        kaoimg = self.handler.get_image_model_cls().create_from_raw(*raw)
        self.assertIsInstance(kaoimg, self.handler.get_image_model_cls())
        self.kao.get(552, 8)
        self.kao.get(1153, 4)
        self.kao.set(552, 8, kaoimg)
        self.kao.set(1153, 4, kaoimg)
        new_kao = self._save_and_reload_main_fixture(self.kao)
        self.assetImagesEqual(kaoimg.get(), new_kao.get(0, 2).get(), rgb_diff=True)
        self.assetImagesNotEqual(kaoimg.get(), new_kao.get(0, 4).get(), rgb_diff=True)
        self.assetImagesEqual(kaoimg.get(), new_kao.get(552, 8).get(), rgb_diff=True)
        self.assetImagesNotEqual(kaoimg.get(), new_kao.get(552, 4).get(), rgb_diff=True)
        self.assetImagesEqual(kaoimg.get(), new_kao.get(1153, 4).get(), rgb_diff=True)
        self.assertIsNone(new_kao.get(1153, 0))

    def test_iterate(self):
        previous_idx = -1
        previous_sidx = -1
        for idx, sidx, kaoimg in self.kao:
            if previous_sidx < 0:
                self.assertEqual(0, sidx)
                self.assertEqual(previous_idx + 1, idx)
                previous_idx = idx
            else:
                self.assertEqual(previous_sidx + 1, sidx)
            if sidx == FIX_IN_LEN_SUB - 1:
                previous_sidx = -1
            else:
                previous_sidx += 1
            if idx in FIX_IN_TEST_MAP:
                if sidx in FIX_IN_TEST_MAP[idx]:
                    self.assetImagesEqual(self._fix_path_png(idx, sidx), kaoimg.get(), rgb_diff=True)
                else:
                    self.assertIsNone(kaoimg)

            self.assertLess(previous_sidx, FIX_IN_LEN_SUB)

        self.assertGreater(previous_idx, -1)
        self.assertLess(previous_idx, FIX_IN_LEN)

    @classmethod
    @fixpath
    def _fix_path_kao(cls):
        return 'fixtures', 'kaomado.kao'

    @classmethod
    @fixpath
    def _fix_path_png(cls, idx, sidx, rgb=False):
        if rgb:
            return 'fixtures', 'rgb', f'{idx:04}', f'{sidx:02}.png'
        return 'fixtures', f'{idx:04}', f'{sidx:02}.png'