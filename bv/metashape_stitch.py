import Metashape
import sys
import os

def main():
    try:
        print("Metashape Stitch v2.2")

        if len(sys.argv) < 3:
            print("ERROR: image_folder output_jpg")
            sys.exit(1)

        image_folder = os.path.abspath(sys.argv[1])
        output_jpg = os.path.abspath(sys.argv[2])

        print("Input:", image_folder)
        print("Output:", output_jpg)

        if not os.path.isdir(image_folder):
            print("ERROR: Folder not found:", image_folder)
            sys.exit(1)

        # Поиск изображений
        images = []
        for f in os.listdir(image_folder):
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.tif')):
                images.append(os.path.join(image_folder, f))

        if len(images) < 2:
            print("ERROR: Need at least 2 images, found:", len(images))
            sys.exit(1)

        print("Found", len(images), "images")

        # Создать проект
        doc = Metashape.Document()
        chunk = doc.addChunk()
        chunk.addPhotos(images)
        print("Added", len(chunk.cameras), "cameras")

        # Сохраняем проект
        project_path = output_jpg.replace('.jpg', '.psx')
        doc.save(path=project_path)

        # Переподключаем chunk после сохранения
        chunk = doc.chunk

        # 1. Выравнивание
        print("1/4 Aligning...")
        chunk.matchPhotos(downscale=1, generic_preselection=True)
        chunk.alignCameras()

        aligned = sum(1 for c in chunk.cameras if c.transform)
        print("Aligned:", aligned, "/", len(chunk.cameras))

        if aligned < 2:
            print("ERROR: Not enough aligned cameras")
            sys.exit(1)

        # 2. Построение карт глубины и модели
        print("2/4 Building depth maps & mesh...")
        chunk.buildDepthMaps(downscale=2)   # MediumQuality
        chunk.buildModel()                  # Arbitrary surface, из Depth Maps

        # Экспорт в OBJ
        print("EXPORT_MODEL_START")
        model_path = output_jpg.replace('.jpg', '_model.obj')
        chunk.exportModel(model_path, format=Metashape.ModelFormatOBJ)
        print("EXPORT_MODEL:" + model_path)

        # 3. Ортомозаика
        print("3/4 Orthomosaic...")
        chunk.buildOrthomosaic(resolution=0.02)

        # Перед экспортом снова получаем актуальный chunk
        chunk = doc.chunk

        # 4. Экспорт ортофото
        print("4/4 Exporting...")
        chunk.exportRaster(output_jpg)

        print("SUCCESS:", output_jpg)
        sys.exit(0)

    except Exception as e:
        print("ERROR:", str(e))
        sys.exit(1)

if __name__ == '__main__':
    main()