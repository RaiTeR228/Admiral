// import axios from 'axios';
// import type { Product } from '@/types/product';
// import { useState, useEffect } from 'react';
// import { FlatList, View, Text } from 'react-native';
// import ProductCard from './ProductCard';

// //создаем обращение к нужному api
// const API_URL_PRODUCTS = 'http://127.0.0.1:8000/api/products/';
// const ProductList = () => {
//     // создаем хук состоние
//     const [products, setProducts] = useState<Product[]>([]);

//     // создаем запрос обращение в бд
//     const getProducts = async () => {
//         const response = await axios.get<Product[]>(API_URL_PRODUCTS);
//         setProducts(response.data);
//     }

//     useEffect(() => {
//         getProducts();
//     }, []);

//     return (
//         <View>
//             <Text>мои продукты</Text>
//             {/* как достаем все данные перебирая массив */}
//             {/* <FlatList
//                 data={products}
//                 keyExtractor={(item) => item.id.toString()}
//                 renderItem={({ item }) => <ProductCard product={item} />}
                
//                 ></FlatList> */}
//         </View>
//     );
// }

// export default ProductList;