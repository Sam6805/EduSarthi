export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-50 border-t border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          {/* About */}
          <div>
            <h3 className="font-bold text-gray-900 mb-4">EduTutor</h3>
            <p className="text-sm text-gray-600">
              AI-powered tutoring for students in remote India. Learn from your textbooks with
              intelligent, easy-to-understand explanations.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="font-bold text-gray-900 mb-4">Quick Links</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>
                <a href="/" className="hover:text-blue-600">
                  Home
                </a>
              </li>
              <li>
                <a href="/tutor" className="hover:text-blue-600">
                  Tutor
                </a>
              </li>
              <li>
                <a href="/upload" className="hover:text-blue-600">
                  Upload Textbooks
                </a>
              </li>
              <li>
                <a href="/metrics" className="hover:text-blue-600">
                  Metrics
                </a>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="font-bold text-gray-900 mb-4">Get in Touch</h3>
            <p className="text-sm text-gray-600">
              Have questions? We'd love to hear from you.
            </p>
            <p className="text-sm text-gray-600 mt-2">info@edututor.in</p>
          </div>
        </div>

        <div className="border-t border-gray-200 pt-8">
          <p className="text-center text-sm text-gray-600">
            © {currentYear} EduTutor. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
