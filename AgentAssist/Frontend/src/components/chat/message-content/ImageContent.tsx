import React, { useState } from 'react';
import { X } from 'lucide-react';

interface ImageContentProps {
  images: Array<{
    url: string;
    alt: string;
    caption?: string;
  }>;
}

const ImageContent: React.FC<ImageContentProps> = ({ images }) => {
  const [expandedImage, setExpandedImage] = useState<string | null>(null);
  
  const handleImageClick = (url: string) => {
    setExpandedImage(url);
  };
  
  const closeExpandedImage = () => {
    setExpandedImage(null);
  };
  
  return (
    <div>
      <div className="grid grid-cols-2 gap-2 mt-2">
        {images.map((image, index) => (
          <div key={index} className="relative">
            <img
              src={image.url}
              alt={image.alt}
              className="rounded-md w-full h-auto object-cover cursor-pointer hover:opacity-90 transition-opacity"
              onClick={() => handleImageClick(image.url)}
              loading="lazy"
            />
            {image.caption && (
              <p className="text-xs mt-1 text-gray-600 dark:text-gray-300">{image.caption}</p>
            )}
          </div>
        ))}
      </div>
      
      {expandedImage && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
          onClick={closeExpandedImage}
        >
          <div className="relative max-w-3xl max-h-[90vh]">
            <button 
              className="absolute top-2 right-2 p-2 bg-black bg-opacity-50 rounded-full text-white hover:bg-opacity-70"
              onClick={(e) => {
                e.stopPropagation();
                closeExpandedImage();
              }}
            >
              <X className="h-5 w-5" />
            </button>
            <img 
              src={expandedImage} 
              alt="Expanded view" 
              className="max-w-full max-h-[90vh] object-contain rounded"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageContent;