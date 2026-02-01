/** Enhanced Markdown renderer with GFM support. */

"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Link from "next/link";

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

/**
 * Normalize markdown links to UI routes.
 * Converts:
 * - ../decisions/005-brownfield-context-extraction.md -> /decisions/005-brownfield-context-extraction
 * - feature-hub-core.md -> /intent/hub-core
 * - ../intent/feature-hub-core.md -> /intent/hub-core
 * - decisions/001-tech-stack.md -> /decisions/001-tech-stack
 */
function normalizeMarkdownLink(href: string | undefined): string | undefined {
  if (!href) return href;
  
  // External links - keep as is
  if (href.startsWith("http://") || href.startsWith("https://") || href.startsWith("mailto:")) {
    return href;
  }
  
  // Anchor links - keep as is
  if (href.startsWith("#")) {
    return href;
  }
  
  // Remove .md extension
  let normalized = href.replace(/\.md$/, "");
  
  // Remove ../ prefix
  normalized = normalized.replace(/^\.\.\//, "");
  
  // Handle decisions links
  if (normalized.startsWith("decisions/")) {
    return `/${normalized}`;
  }
  
  // Handle intent links
  if (normalized.startsWith("intent/")) {
    // Remove intent/ prefix and feature- prefix if present
    const name = normalized.replace(/^intent\//, "").replace(/^feature-/, "");
    return `/intent/${name}`;
  }
  
  // Handle feature- prefixed files (intents)
  if (normalized.startsWith("feature-")) {
    const name = normalized.replace(/^feature-/, "");
    return `/intent/${name}`;
  }
  
  // Handle decision files (001-name format)
  if (/^\d{3}-/.test(normalized)) {
    return `/decisions/${normalized}`;
  }
  
  // If it's just a filename without path, try to infer type
  // This handles cases like "project-intent.md" -> "/intent/project"
  if (normalized === "project-intent") {
    return "/intent/project";
  }
  
  // Default: assume it's a relative path that should stay relative
  // or return as-is if it's already a valid route
  if (normalized.startsWith("/")) {
    return normalized;
  }
  
  // For unknown patterns, return as-is (might be a valid route)
  return normalized;
}

export function MarkdownRenderer({ content, className = "" }: MarkdownRendererProps) {
  return (
    <div className={`markdown-content ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Custom heading rendering with anchors
          h1: ({ children }) => (
            <h1 className="text-3xl font-bold text-gray-900 mb-4 pb-2 border-b border-gray-200">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-2xl font-semibold text-gray-800 mt-8 mb-3 pb-1 border-b border-gray-100">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-2">
              {children}
            </h3>
          ),
          h4: ({ children }) => (
            <h4 className="text-lg font-medium text-gray-700 mt-4 mb-2">
              {children}
            </h4>
          ),
          // Paragraphs
          p: ({ children }) => (
            <p className="text-gray-700 leading-relaxed mb-4">
              {children}
            </p>
          ),
          // Lists
          ul: ({ children }) => (
            <ul className="list-disc list-inside space-y-1 mb-4 text-gray-700 ml-4">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal list-inside space-y-1 mb-4 text-gray-700 ml-4">
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li className="text-gray-700 leading-relaxed">
              {children}
            </li>
          ),
          // Links
          a: ({ href, children }) => {
            const normalizedHref = normalizeMarkdownLink(href);
            const isExternal = normalizedHref?.startsWith("http://") || normalizedHref?.startsWith("https://");
            const isAnchor = normalizedHref?.startsWith("#");
            
            // Use Next.js Link for internal navigation
            if (normalizedHref && !isExternal && !isAnchor && normalizedHref.startsWith("/")) {
              return (
                <Link
                  href={normalizedHref}
                  className="text-blue-600 hover:text-blue-800 underline"
                >
                  {children}
                </Link>
              );
            }
            
            // External links or anchors use regular <a> tag
            return (
              <a
                href={normalizedHref || href}
                className="text-blue-600 hover:text-blue-800 underline"
                target={isExternal ? "_blank" : undefined}
                rel={isExternal ? "noopener noreferrer" : undefined}
              >
                {children}
              </a>
            );
          },
          // Code blocks
          code: ({ className, children, ...props }) => {
            const isInline = !className;
            if (isInline) {
              return (
                <code className="bg-gray-100 text-gray-800 px-1.5 py-0.5 rounded text-sm font-mono">
                  {children}
                </code>
              );
            }
            return (
              <code className={`${className} block`} {...props}>
                {children}
              </code>
            );
          },
          pre: ({ children }) => (
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto mb-4 text-sm">
              {children}
            </pre>
          ),
          // Blockquotes
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-blue-500 pl-4 py-2 my-4 bg-blue-50 text-gray-700 italic rounded-r">
              {children}
            </blockquote>
          ),
          // Tables (GFM)
          table: ({ children }) => (
            <div className="overflow-x-auto mb-4">
              <table className="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-gray-50">
              {children}
            </thead>
          ),
          tbody: ({ children }) => (
            <tbody className="divide-y divide-gray-200 bg-white">
              {children}
            </tbody>
          ),
          tr: ({ children }) => (
            <tr className="hover:bg-gray-50">
              {children}
            </tr>
          ),
          th: ({ children }) => (
            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="px-4 py-3 text-sm text-gray-700">
              {children}
            </td>
          ),
          // Horizontal rule
          hr: () => (
            <hr className="my-8 border-t border-gray-200" />
          ),
          // Strong and emphasis
          strong: ({ children }) => (
            <strong className="font-semibold text-gray-900">
              {children}
            </strong>
          ),
          em: ({ children }) => (
            <em className="italic text-gray-700">
              {children}
            </em>
          ),
          // Task lists (GFM checkboxes)
          input: ({ type, checked, ...props }) => {
            if (type === "checkbox") {
              return (
                <input
                  type="checkbox"
                  checked={checked}
                  readOnly
                  className="mr-2 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  {...props}
                />
              );
            }
            return <input type={type} {...props} />;
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
