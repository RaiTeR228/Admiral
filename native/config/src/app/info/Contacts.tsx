import { View, Text,Button } from "react-native";
import InfoPageList from "@/components/InfoPageList";
import {router} from "expo-router";
import { useRouter } from 'expo-router';

const Contacts =()=>{
    const router = useRouter();
    return(<View>
    <InfoPageList slug="contacts" />
    <Button title="Go to Contacts" onPress={() => router.back()}/>
</View>)}

export default Contacts;