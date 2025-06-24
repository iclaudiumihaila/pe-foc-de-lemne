import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useCartContext } from '../contexts/CartContext';
import ProductCard from '../components/product/ProductCard';
import MetaTags from '../components/SEO/MetaTags';
import { BreadcrumbStructuredData } from '../components/SEO/StructuredData';
import { SEO_TEMPLATES } from '../data/seoTemplates';

const Home = () => {
  const { addToCart, formatPrice } = useCartContext();
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  // Mock featured products data (will be replaced with API call)
  useEffect(() => {
    const mockFeaturedProducts = [
      {
        id: 'featured-1',
        name: 'Roșii ecologice',
        price: 8.50,
        image: '/images/tomatoes.jpg',
        category: 'Legume',
        isOrganic: true,
        inStock: true,
        unit: 'kg',
        description: 'Roșii crescute natural, fără pesticide'
      },
      {
        id: 'featured-2', 
        name: 'Miere de salcâm',
        price: 25.00,
        image: '/images/honey.jpg',
        category: 'Produse apicole',
        isOrganic: true,
        inStock: true,
        unit: 'borcan 500g',
        description: 'Miere pură de salcâm din apiarii locale'
      },
      {
        id: 'featured-3',
        name: 'Brânză de țară',
        price: 15.00,
        image: '/images/cheese.jpg',
        category: 'Lactate',
        isOrganic: false,
        inStock: true,
        unit: 'kg',
        description: 'Brânză tradițională din lapte de vacă'
      },
      {
        id: 'featured-4',
        name: 'Ouă de țară',
        price: 12.00,
        image: '/images/eggs.jpg',
        category: 'Ouă',
        isOrganic: true,
        inStock: true,
        unit: '10 bucăți',
        description: 'Ouă proaspete de la găini crescute în curte'
      }
    ];

    // Simulate loading delay
    setTimeout(() => {
      setFeaturedProducts(mockFeaturedProducts);
      setLoading(false);
    }, 500);
  }, []);

  const handleAddToCart = (product) => {
    addToCart(product, 1);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* SEO Meta Tags */}
      <MetaTags {...SEO_TEMPLATES.home} />
      
      {/* Breadcrumb Structured Data */}
      <BreadcrumbStructuredData 
        breadcrumbs={[
          { name: 'Acasă', url: '/' }
        ]} 
      />
      {/* Hero Section */}
      <section className="bg-green-600 text-white py-16 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            🌱 Pe Foc de Lemne
          </h1>
          <p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto">
            Produse locale și naturale, direct de la producători din comunitatea noastră.
            Susține agricultura locală și bucură-te de gustul autentic!
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/products"
              className="bg-white text-green-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition-colors min-h-[44px] flex items-center justify-center"
            >
              Explorează produsele
            </Link>
            <a
              href="#featured"
              className="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white hover:text-green-600 transition-colors min-h-[44px] flex items-center justify-center"
            >
              Vezi ofertele
            </a>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-800 mb-12">
            De ce să alegi produsele locale?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center bg-white p-6 rounded-lg shadow-sm">
              <div className="text-4xl mb-4">🌿</div>
              <h3 className="text-xl font-semibold text-gray-800 mb-3">
                Naturale și proaspete
              </h3>
              <p className="text-gray-600">
                Produse crescute fără chimicale, culese la maturitate și livrate direct de la producător.
              </p>
            </div>
            <div className="text-center bg-white p-6 rounded-lg shadow-sm">
              <div className="text-4xl mb-4">🚚</div>
              <h3 className="text-xl font-semibold text-gray-800 mb-3">
                Livrare locală
              </h3>
              <p className="text-gray-600">
                Transport scurt, impact redus asupra mediului și produse care ajung mai rapid la tine.
              </p>
            </div>
            <div className="text-center bg-white p-6 rounded-lg shadow-sm">
              <div className="text-4xl mb-4">🤝</div>
              <h3 className="text-xl font-semibold text-gray-800 mb-3">
                Comunitate locală
              </h3>
              <p className="text-gray-600">
                Susții familiile de fermieri din zona ta și contribui la dezvoltarea economiei locale.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Products Section */}
      <section id="featured" className="py-16 px-4 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-800 mb-4">
              Produse recomandate
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Descoperă o selecție specială de produse locale, alese pentru calitatea și 
              prospețimea lor excepțională.
            </p>
          </div>

          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {[...Array(4)].map((_, index) => (
                <div key={index} className="bg-gray-200 rounded-lg h-80 animate-pulse" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {featuredProducts.map((product) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  onAddToCart={handleAddToCart}
                />
              ))}
            </div>
          )}

          <div className="text-center mt-8">
            <Link
              to="/products"
              className="bg-green-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors inline-flex items-center justify-center min-h-[44px]"
            >
              Vezi toate produsele
            </Link>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-16 px-4 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-800 mb-12">
            Cum funcționează?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🛒</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                1. Alege produsele
              </h3>
              <p className="text-gray-600">
                Explorează catalogul și adaugă în coș produsele dorite
              </p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">📱</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                2. Verificare SMS
              </h3>
              <p className="text-gray-600">
                Confirmă comanda prin verificarea numărului de telefon
              </p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🚚</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                3. Livrare locală
              </h3>
              <p className="text-gray-600">
                Produsele ajung direct la tine, proaspete și naturale
              </p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">😊</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                4. Bucură-te!
              </h3>
              <p className="text-gray-600">
                Savurează gustul autentic al produselor locale
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action Section */}
      <section className="py-16 px-4 bg-green-600 text-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-6">
            Începe să comanzi astăzi!
          </h2>
          <p className="text-xl mb-8">
            Alătură-te comunității noastre și susține producătorii locali. 
            Livrare gratuită pentru comenzile peste {formatPrice(50)}.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/products"
              className="bg-white text-green-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition-colors min-h-[44px] flex items-center justify-center"
            >
              Comandă acum
            </Link>
            <Link
              to="/cart"
              className="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white hover:text-green-600 transition-colors min-h-[44px] flex items-center justify-center"
            >
              Vezi coșul
            </Link>
          </div>
        </div>
      </section>

      {/* Footer Info */}
      <footer className="bg-gray-800 text-white py-8 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <h3 className="text-lg font-semibold mb-4">Pe Foc de Lemne</h3>
          <p className="text-gray-300 mb-4">
            Conectând comunitatea cu producătorii locali pentru o alimentație mai sănătoasă și sustenabilă.
          </p>
          <div className="flex justify-center gap-6 text-sm text-gray-400">
            <span>📧 contact@pefocdelemne.ro</span>
            <span>📞 0700 123 456</span>
            <span>📍 România</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home;