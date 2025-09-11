import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

class UrlViewer extends StatelessWidget {
  final String url;
  final String title;

  const UrlViewer({super.key, required this.url, required this.title});

  @override
  Widget build(BuildContext context) {
    return ExpansionTile(
      title: Text(title),
      children: [
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: InkWell(
            onTap: () async {
              final uri = Uri.parse(url);
              if (await canLaunchUrl(uri)) {
                await launchUrl(uri);
              } else {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Could not launch $url'), backgroundColor: Colors.red),
                );
              }
            },
            child: Text(
              url,
              style: const TextStyle(color: Colors.blue, decoration: TextDecoration.underline),
            ),
          ),
        ),
      ],
    );
  }
}
