import { Textbook, UploadedFile } from '@/types';

export const TEXTBOOKS: Textbook[] = [
  { id: 'class6-science',     name: 'Class 6 Science',      class: '6',  subject: 'Science',      chapters: 16 },
  { id: 'class7-geography',   name: 'Class 7 Geography',    class: '7',  subject: 'Geography',    chapters: 18 },
  { id: 'class8-mathematics', name: 'Class 8 Mathematics',  class: '8',  subject: 'Mathematics',  chapters: 16 },
  { id: 'class8-science',     name: 'Class 8 Science',      class: '8',  subject: 'Science',      chapters: 18 },
  { id: 'class9-history',     name: 'Class 9 History',      class: '9',  subject: 'History',      chapters: 15 },
  { id: 'class10-english',    name: 'Class 10 English',     class: '10', subject: 'English',      chapters: 20 },
];

// No fake default uploads — only real user uploads shown
export const UPLOADED_TEXTBOOKS: UploadedFile[] = [];
