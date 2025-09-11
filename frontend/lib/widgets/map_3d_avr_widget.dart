import 'package:flutter/material.dart';
import 'package:model_viewer_plus/model_viewer_plus.dart';

class Map3dAvrWidget extends StatelessWidget {
  final String modelUrl;

  const Map3dAvrWidget({super.key, required this.modelUrl});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        SizedBox(
          height: 600,
          child: ModelViewer(
            src: modelUrl,
            alt: "A 3D model of a building",
            ar: true,
            autoRotate: true,
            cameraControls: true,
          ),
        ),
        ElevatedButton(
          onPressed: () {
            // TODO: Implement AVR mode
          },
          child: const Text("Launch AVR Mode"),
        ),
      ],
    );
  }
}
