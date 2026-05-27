import { View, Text,Button } from "react-native";
import InfoPageList from "@/components/InfoPageList"; 
import {router} from "expo-router";
import { useRouter } from 'expo-router';

const About =()=>{
    const router = useRouter();
    return(<View>
    <InfoPageList slug="about" />
    <Button title="Go to About" onPress={() => router.back()}/>
</View>)}

export default About;