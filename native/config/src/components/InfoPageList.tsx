// import React, { useEffect, useState } from 'react';
// import { View, Text, FlatList, ActivityIndicator } from 'react-native';
// import axios from 'axios';

// const API_URLS_INFO = "http://localhost:8000/api2/info-pages/"

// interface InfoPageType {
//   id: number;
//   title: string;
//   body: string;
// }

// // Добавляем slug в пропсы компонента
// const InfoPageList = ({ slug }: { slug: string }) => {
//   const [posts, setPosts] = useState<InfoPageType[]>([]);
//   const [loading, setLoading] = useState(true);

//   useEffect(() => {
//     // Теперь slug определен
//     axios.get<InfoPageType[]>(`${API_URLS_INFO}${slug}/`)
//       .then(response => {
//         setPosts(response.data);
//         setLoading(false);
//       })
//       .catch(error => {
//         console.error(error);
//         setLoading(false);
//       });
//   }, [slug]); // Добавляем slug в зависимости

//   if (loading) return <ActivityIndicator size="large" />;

//   return (
//     <View>
//       <FlatList
//         data={posts}
//         keyExtractor={item => item.id.toString()}
//         renderItem={({ item }) => (
//           <View style={{ padding: 10 }}>
//             <Text style={{ fontWeight: 'bold' }}>{item.title}</Text>
//             <Text>{item.body}</Text>
//           </View>
//         )}
//       />
//     </View>
//   );
// };

// export default InfoPageList;


import type { InfoPage } from "@/types/InfoPage";
import axios from "axios";
import React, { useEffect, useState } from "react";
import { View, Text } from "react-native";

const API_URLS_INFO = "http://127.0.0.1:8000/api2/info-pages/"
type Props = {
    slug: string;
}

const infoPageList =({ slug }: Props) => {
    const [page, setPage] = useState<InfoPage | null>(null);
    const getPage = async () => {
        const response = await axios.get<InfoPage>(`${API_URLS_INFO}${slug}/`);
        setPage(response.data);
    };
    useEffect(() => {
        getPage();
    }, []);
    if (!page) return <View><Text>Loading...</Text></View>;
    return (
        <View>
            <Text style={{ fontWeight: 'bold' }}>{page.slug}</Text>
            {/* <Text style={{ fontWeight: 'bold' }}>{page.title}</Text> */}
            <Text style={{ fontWeight: 'bold' }}>{page.text}</Text>
        </View>
    )
};

export default infoPageList;