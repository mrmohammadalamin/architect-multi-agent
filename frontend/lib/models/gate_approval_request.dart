class GateApprovalRequest {
  final String approvedBy;
  final String comments;
  final bool approved;

  GateApprovalRequest({
    required this.approvedBy,
    required this.comments,
    this.approved = true,
  });

  Map<String, dynamic> toJson() {
    return {
      'approved_by': approvedBy,
      'comments': comments,
      'approved': approved,
    };
  }
}
