class Artifact {
  final String name;
  final String type;
  final dynamic content;
  final String? url;

  Artifact({required this.name, required this.type, this.content, this.url});

  factory Artifact.fromJson(Map<String, dynamic> json) {
    return Artifact(
      name: json['name'],
      type: json['type'],
      content: json['content'],
      url: json['url'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'type': type,
      'content': content,
      'url': url,
    };
  }
}
