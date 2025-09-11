import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

class SvgViewer extends StatelessWidget {
  final String svgContent;
  final String title;

  const SvgViewer({super.key, required this.svgContent, required this.title});

  @override
  Widget build(BuildContext context) {
    return ExpansionTile(
      title: Text(title),
      children: [
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: SvgPicture.string(
            svgContent,
            width: MediaQuery.of(context).size.width * 0.8,
            fit: BoxFit.contain,
          ),
        ),
      ],
    );
  }
}
