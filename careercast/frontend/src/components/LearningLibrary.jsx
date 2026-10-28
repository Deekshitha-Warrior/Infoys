import React, { useState } from "react";
import { ArrowUpRight, BookOpen, Award } from "lucide-react";

export const learningCourses = [
  [
    "Google’s Python Class",
    "Practice Python with lessons, videos, and coding exercises.",
    "https://developers.google.com/edu/python"
  ],
  [
    "Introduction to Machine Learning",
    "Understand what machine learning can do and when to use it.",
    "https://developers.google.com/machine-learning/intro-to-ml"
  ],
  [
    "Machine Learning Crash Course",
    "Build foundations through interactive lessons and exercises.",
    "https://developers.google.com/machine-learning/crash-course"
  ],
  [
    "ML Problem Framing",
    "Turn a real-world problem into a machine learning task.",
    "https://developers.google.com/machine-learning/problem-framing"
  ],
  [
    "Managing ML Projects",
    "Plan and manage a machine learning project.",
    "https://developers.google.com/machine-learning/managing-ml-projects"
  ],
  [
    "Decision Forests",
    "Explore decision trees and forest-based models.",
    "https://developers.google.com/machine-learning/decision-forests"
  ],
  [
    "Recommendation Systems",
    "Learn the foundations of personalized recommendations.",
    "https://developers.google.com/machine-learning/recommendation"
  ],
  [
    "Clustering",
    "Group related examples with unsupervised learning.",
    "https://developers.google.com/machine-learning/clustering"
  ],
  [
    "Generative Adversarial Networks",
    "Explore how GANs learn to generate new examples.",
    "https://developers.google.com/machine-learning/gan"
  ],
  [
    "Technical Writing One",
    "Write clearer explanations and technical documentation.",
    "https://developers.google.com/tech-writing/one"
  ]
];
export const learningCertificates = [
  [
    "Google Data Analytics",
    "Build skills in analysis, spreadsheets, SQL, and visualization.",
    "https://grow.google/certificates/data-analytics/"
  ],
  [
    "Google Advanced Data Analytics",
    "Develop advanced analytical and machine learning skills.",
    "https://grow.google/certificates/advanced-data-analytics/"
  ],
  [
    "Google Business Intelligence",
    "Explore dashboards, data models, and business insights.",
    "https://grow.google/certificates/business-intelligence/"
  ],
  [
    "Google Cybersecurity",
    "Develop foundations for identifying and responding to threats.",
    "https://grow.google/certificates/cybersecurity/"
  ],
  [
    "Google IT Support",
    "Learn troubleshooting, systems, and IT support fundamentals.",
    "https://grow.google/certificates/it-support/"
  ],
  [
    "Google IT Automation with Python",
    "Apply Python and automation to practical IT tasks.",
    "https://grow.google/certificates/it-automation-python/"
  ],
  [
    "Google Project Management",
    "Learn to plan, organize, and deliver projects.",
    "https://grow.google/certificates/project-management/"
  ],
  [
    "Google UX Design",
    "Explore research, prototyping, and user-centered design.",
    "https://grow.google/certificates/ux-design/"
  ],
  [
    "Google Digital Marketing & E-commerce",
    "Develop digital marketing and online commerce skills.",
    "https://grow.google/certificates/digital-marketing-ecommerce/"
  ],
  [
    "Google Cloud Digital Leader",
    "Explore the certification requirements and preparation for cloud fundamentals.",
    "https://cloud.google.com/learn/certification/cloud-digital-leader"
  ]
];

export default function LearningLibrary() {
  const [category, setCategory] = useState("courses");
  const courses = category === "courses";
  const items = courses ? learningCourses : learningCertificates;
  return (
    <section className="panel learning-library" aria-labelledby="learning-library-title">
      <div className="learning-library-heading">
        <div>
          <span className="eyebrow">LEARN WITH GOOGLE</span>
          <h2 id="learning-library-title">Invest in your next chapter</h2>
          <p className="muted">10 courses and 10 certificate or certification pathways from official Google resources.</p>
        </div>
        <div className="learning-library-switch" role="group" aria-label="Resource category">
          <button type="button" aria-pressed={courses} onClick={() => setCategory("courses")}><BookOpen size={16} /> Courses · 10</button>
          <button type="button" aria-pressed={!courses} onClick={() => setCategory("certificates")}><Award size={16} /> Certifications · 10</button>
        </div>
      </div>
      <p className="data-note">{courses
        ? "Self-study resources. Opening or finishing a course here does not award a certification."
        : "Certificate programs and an exam-based certification. Check the provider for prerequisites, enrollment fees, and assessment requirements."}</p>
      <div className="learning-library-cards">
        {items.map(([title, description, url], index) => (
          <article className="learning-library-card" key={url}>
            <div className="learning-library-meta"><span className="lavender-pill">{courses ? "Course" : index === 9 ? "Certification exam" : "Certificate program"}</span><small>{String(index + 1).padStart(2, "0")}</small></div>
            <h3>{title}</h3>
            <p className="muted">{description}</p>
            <a href={url} target="_blank" rel="noopener noreferrer" aria-label={`Explore ${title} (opens in a new tab)`}>Explore {courses ? "course" : "credential"}<ArrowUpRight size={16} /></a>
          </article>
        ))}
      </div>
    </section>
  );
}
