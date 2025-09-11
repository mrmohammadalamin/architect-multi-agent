import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:frontend/models/project_status.dart';
import 'package:frontend/services/api_service.dart';

abstract class WorkflowEvent {}

class LoadWorkflow extends WorkflowEvent {
  final String projectId;

  LoadWorkflow(this.projectId);
}

abstract class WorkflowState {}

class WorkflowInitial extends WorkflowState {}

class WorkflowLoading extends WorkflowState {}

class WorkflowLoaded extends WorkflowState {
  final ProjectStatus projectStatus;

  WorkflowLoaded(this.projectStatus);
}

class WorkflowError extends WorkflowState {
  final String message;

  WorkflowError(this.message);
}

class WorkflowBloc extends Bloc<WorkflowEvent, WorkflowState> {
  final ApiService apiService;

  WorkflowBloc(this.apiService) : super(WorkflowInitial()) {
    on<LoadWorkflow>((event, emit) async {
      emit(WorkflowLoading());
      try {
        final projectStatus = await apiService.getProjectStatus(event.projectId);
        emit(WorkflowLoaded(projectStatus));
      } catch (e) {
        emit(WorkflowError(e.toString()));
      }
    });
  }
}
