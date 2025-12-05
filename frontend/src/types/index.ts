export type JobStatus =
    | 'QUEUED'
    | 'PROCESSING_IMAGES'
    | 'GENERATING_STORY'
    | 'GENERATING_IMAGE'
    | 'UPLOADING'
    | 'COMPLETED'
    | 'FAILED';

export interface JobResponse {
    job_id: string;
    status: JobStatus;
    result_url: string | null;
    error_message: string | null;
}
