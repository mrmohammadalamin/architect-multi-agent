import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';

class Plan2dWidget extends StatelessWidget {
  final String imageUrl;

  const Plan2dWidget({super.key, required this.imageUrl});

  @override
  Widget build(BuildContext context) {
    return InteractiveViewer(
      child: CachedNetworkImage(
        imageUrl: imageUrl,
        placeholder: (context, url) => const CircularProgressIndicator(),
        errorWidget: (context, url, error) => const Icon(Icons.error),
      ),
    );
  }
}
